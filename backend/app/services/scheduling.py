"""Server-side scheduling rules; PostgreSQL EXCLUDE constraint handles the race at commit."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Court, CourtAllocation, MaintenanceWindow

VN = ZoneInfo('Asia/Ho_Chi_Minh')


def utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)  # SQLite returns naive UTC values
    return value.astimezone(timezone.utc)


def lock_court(db: Session, court_id: int):
    """Serialize all booking, tournament scheduling, maintenance and hour edits per court."""
    db.execute(select(Court.id).where(Court.id == court_id).with_for_update()).scalar_one_or_none()
    court = db.get(Court, court_id)
    if court is not None:
        # A concurrent transaction may have inserted maintenance or edited operating hours.
        # Invalidate eager-loaded relationships after acquiring the row lock.
        db.expire(court, ["operating_hours", "maintenance_windows"])


def check_interval(db: Session, court: Court, start: datetime, end: datetime, *, ignore_allocation_id: int | None = None, check_future: bool = True):
    if not court.active:
        raise HTTPException(409, 'Sân đang tạm ngừng hoạt động')
    if start.tzinfo is None or end.tzinfo is None:
        raise HTTPException(422, 'Thời gian phải có múi giờ, ví dụ +07:00')
    start, end = utc(start), utc(end)
    if start >= end or (end - start) > timedelta(hours=4):
        raise HTTPException(422, 'Thời lượng phải lớn hơn 0 và không quá 4 giờ')
    if check_future and start <= datetime.now(timezone.utc):
        raise HTTPException(422, 'Chỉ được chọn khung giờ trong tương lai')
    local_start, local_end = start.astimezone(VN), end.astimezone(VN)
    if local_start.date() != local_end.date():
        raise HTTPException(422, 'Không thể đặt sân qua ngày')
    length_minutes = int((end - start).total_seconds() // 60)
    if length_minutes < court.min_duration_minutes or length_minutes % 30:
        raise HTTPException(422, 'Thời lượng không hợp lệ (tối thiểu theo sân và bội số 30 phút)')
    hours = next((x for x in court.operating_hours if x.weekday == local_start.weekday()), None)
    if not hours or local_start.time().replace(tzinfo=None) < hours.open_time or local_end.time().replace(tzinfo=None) > hours.close_time:
        raise HTTPException(409, 'Ngoài giờ mở cửa của sân')
    for m in court.maintenance_windows:
        if start < utc(m.end_at) and end > utc(m.start_at):
            raise HTTPException(409, 'Trùng lịch bảo trì sân')
    # This check improves error messages; PostgreSQL EXCLUDE constraint is the concurrency guard.
    query = select(CourtAllocation).where(
        CourtAllocation.court_id == court.id, CourtAllocation.active.is_(True),
        CourtAllocation.start_at < end + timedelta(minutes=court.buffer_minutes),
        CourtAllocation.end_at > start,
    )
    # Allocations include the buffer following prior reservations.
    if ignore_allocation_id is not None:
        query = query.where(CourtAllocation.id != ignore_allocation_id)
    if db.scalar(query) is not None:
        raise HTTPException(409, 'Khung giờ đã có người đặt hoặc có lịch thi đấu')
    return start, end


def fee(court: Court, start: datetime, end: datetime) -> Decimal:
    hours = Decimal(int((end-start).total_seconds() // 60)) / Decimal(60)
    return (court.price_per_hour * hours).quantize(Decimal('0.01'))


def notify(db: Session, user_id: int, title: str, message: str):
    from app.models import Notification
    db.add(Notification(user_id=user_id, title=title, message=message))


def is_overlap_error(exc: Exception) -> bool:
    # PostgreSQL ExclusionViolation = SQLSTATE 23P01.
    orig = getattr(exc, 'orig', None)
    return getattr(orig, 'sqlstate', None) == '23P01' or 'no_active_allocation_overlap' in str(exc)


def conflict_from_db(exc: Exception) -> HTTPException:
    return HTTPException(409, 'Khung giờ vừa được người khác đặt. Hãy chọn thời gian khác.') if is_overlap_error(exc) else HTTPException(409, 'Dữ liệu xung đột hoặc đang được cập nhật')
