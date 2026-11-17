from datetime import date as Date, datetime, time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.security import get_current_user, require_roles
from app.db.session import get_db
from app.models import Court, CourtAllocation, MaintenanceWindow, OperatingHour, Sport, User, UserRole
from app.services.scheduling import lock_court, utc
from app.schemas import (
    AvailabilityOut, CourtCreate, CourtDetailOut, CourtListOut, CourtOut, CourtPatch,
    MaintenanceIn, MaintenanceOut, OperatingHourIn, OperatingHourOut, SlotOut,
)

router = APIRouter(prefix="/courts", tags=["Courts"])
VIETNAM_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def court_stmt():
    return select(Court).options(
        selectinload(Court.sport), selectinload(Court.operating_hours),
        selectinload(Court.maintenance_windows),
    )


def owned_court(court_id: int, user: User, db: Session) -> Court:
    court = db.scalar(court_stmt().where(Court.id == court_id))
    if not court:
        raise HTTPException(404, "Không tìm thấy sân")
    if user.role != UserRole.ADMIN and court.owner_id != user.id:
        raise HTTPException(403, "Bạn không sở hữu sân này")
    return court


def validate_sport(db: Session, sport_id: int):
    sport = db.get(Sport, sport_id)
    if sport is None or not sport.active:
        raise HTTPException(422, "Môn thể thao không tồn tại hoặc đang bị khóa")


@router.get("", response_model=CourtListOut)
def list_courts(
    q: str | None = Query(None, max_length=100),
    sport_id: int | None = None,
    district: str | None = Query(None, max_length=100),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    limit: int = Query(12, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(422, "Giá thấp nhất không thể lớn hơn giá cao nhất")
    base = select(Court).join(Sport).where(Court.active.is_(True), Sport.active.is_(True))
    if q:
        term = f"%{q.strip()}%"
        base = base.where(or_(Court.name.ilike(term), Court.address.ilike(term)))
    if sport_id is not None:
        base = base.where(Court.sport_id == sport_id)
    if district:
        base = base.where(Court.district.ilike(f"%{district.strip()}%"))
    if min_price is not None:
        base = base.where(Court.price_per_hour >= min_price)
    if max_price is not None:
        base = base.where(Court.price_per_hour <= max_price)
    total = db.scalar(select(func.count()).select_from(base.order_by(None).subquery())) or 0
    items = db.scalars(base.options(selectinload(Court.sport)).order_by(Court.id.desc()).limit(limit).offset(offset)).all()
    return CourtListOut(items=[CourtOut.model_validate(i) for i in items], total=total)


@router.get("/mine", response_model=list[CourtDetailOut])
def my_courts(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN))):
    statement = court_stmt().order_by(Court.id.desc())
    if user.role != UserRole.ADMIN:
        statement = statement.where(Court.owner_id == user.id)
    return db.scalars(statement).all()


@router.get("/{court_id}", response_model=CourtDetailOut)
def get_court(court_id: int, db: Session = Depends(get_db)):
    court = db.scalar(court_stmt().where(Court.id == court_id, Court.active.is_(True)))
    if not court:
        raise HTTPException(404, "Không tìm thấy sân")
    return court


@router.post("", response_model=CourtDetailOut, status_code=201)
def create_court(
    body: CourtCreate, db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
):
    validate_sport(db, body.sport_id)
    court = Court(**body.model_dump(), owner_id=user.id)
    court.operating_hours = [OperatingHour(weekday=d, open_time=time(6), close_time=time(22)) for d in range(7)]
    db.add(court)
    db.commit()
    return db.scalar(court_stmt().where(Court.id == court.id))


@router.patch("/{court_id}", response_model=CourtDetailOut)
def update_court(
    court_id: int, body: CourtPatch, db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
):
    court = owned_court(court_id, user, db)
    data = body.model_dump(exclude_unset=True)
    if any(value is None for value in data.values()):
        raise HTTPException(422, "Trường cập nhật không thể null")
    if "sport_id" in data:
        validate_sport(db, data["sport_id"])
    for field, value in data.items():
        setattr(court, field, value)
    db.commit()
    return db.scalar(court_stmt().where(Court.id == court_id))


@router.put("/{court_id}/hours", response_model=list[OperatingHourOut])
def set_operating_hours(
    court_id: int, hours: list[OperatingHourIn], db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
):
    court = owned_court(court_id, user, db)
    lock_court(db, court_id)
    if len(hours) > 7 or len({h.weekday for h in hours}) != len(hours):
        raise HTTPException(422, "Mỗi thứ trong tuần chỉ được có một khoảng giờ")
    # Preserve booked/allocated future slots when changing opening hours.
    new_hours = {h.weekday: h for h in hours}
    existing_allocations = db.scalars(select(CourtAllocation).where(
        CourtAllocation.court_id==court_id,CourtAllocation.active.is_(True),
        CourtAllocation.end_at > datetime.now(timezone.utc)
    )).all()
    for a in existing_allocations:
        begins=ensure_utc(a.start_at).astimezone(VIETNAM_TZ)
        finishes=ensure_utc(a.end_at).astimezone(VIETNAM_TZ)
        allowed=new_hours.get(begins.weekday())
        if not allowed or begins.date()!=finishes.date() or begins.time().replace(tzinfo=None)<allowed.open_time or finishes.time().replace(tzinfo=None)>allowed.close_time:
            raise HTTPException(409,"Giờ mở cửa mới sẽ xung đột với lịch đặt sân hoặc trận đấu hiện có")
    # Flush deletion first to avoid UNIQUE(court_id, weekday) conflicts on replacement.
    db.execute(delete(OperatingHour).where(OperatingHour.court_id == court_id))
    db.flush()
    db.expire(court, ["operating_hours"])
    court.operating_hours = [OperatingHour(**h.model_dump()) for h in hours]
    db.commit()
    return db.scalar(court_stmt().where(Court.id == court_id)).operating_hours


@router.post("/{court_id}/maintenance", response_model=MaintenanceOut, status_code=201)
def create_maintenance(
    court_id: int, body: MaintenanceIn, db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
):
    owned_court(court_id, user, db)
    lock_court(db, court_id)
    data = body.model_dump()
    data["start_at"] = data["start_at"].astimezone(timezone.utc)
    data["end_at"] = data["end_at"].astimezone(timezone.utc)
    # Prevent new maintenance from invalidating existing paid/confirmed reservations or matches.
    overlapping = db.scalar(select(CourtAllocation.id).where(
        CourtAllocation.court_id == court_id, CourtAllocation.active.is_(True),
        CourtAllocation.start_at < data["end_at"], CourtAllocation.end_at > data["start_at"]
    ).limit(1))
    if overlapping is not None:
        raise HTTPException(409, "Lịch bảo trì trùng với đơn đặt sân hoặc trận đấu")
    row = MaintenanceWindow(court_id=court_id, **data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{court_id}/maintenance/{maintenance_id}", status_code=204)
def delete_maintenance(
    court_id: int, maintenance_id: int, db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
):
    owned_court(court_id, user, db)
    row = db.get(MaintenanceWindow, maintenance_id)
    if row is None or row.court_id != court_id:
        raise HTTPException(404, "Không tìm thấy lịch bảo trì")
    db.delete(row)
    db.commit()


def ensure_utc(dt: datetime) -> datetime:
    # SQLite drops tzinfo in tests; datetime values are written as UTC in PostgreSQL.
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


@router.get("/{court_id}/availability", response_model=AvailabilityOut)
def get_availability(
    court_id: int,
    date: Date,
    duration_minutes: int | None = Query(None, ge=30, le=240, multiple_of=30),
    db: Session = Depends(get_db),
):
    court = db.scalar(court_stmt().where(Court.id == court_id, Court.active.is_(True)))
    if court is None:
        raise HTTPException(404, "Không tìm thấy sân")
    minutes = duration_minutes if duration_minutes is not None else court.min_duration_minutes
    if minutes < court.min_duration_minutes:
        raise HTTPException(422, "Thời gian đặt nhỏ hơn thời gian tối thiểu")
    hours = next((h for h in court.operating_hours if h.weekday == date.weekday()), None)
    if hours is None:
        return AvailabilityOut(court_id=court_id, date=date, duration_minutes=minutes, slots=[])
    opening = datetime.combine(date, hours.open_time, tzinfo=VIETNAM_TZ)
    closing = datetime.combine(date, hours.close_time, tzinfo=VIETNAM_TZ)
    now = datetime.now(VIETNAM_TZ)
    occupied = db.scalars(select(CourtAllocation).where(
        CourtAllocation.court_id == court_id, CourtAllocation.active.is_(True),
        CourtAllocation.start_at < ensure_utc(closing) + timedelta(minutes=court.buffer_minutes),
        CourtAllocation.end_at > ensure_utc(opening)
    )).all()
    slots = []
    cursor = opening
    while cursor + timedelta(minutes=minutes) <= closing:
        end = cursor + timedelta(minutes=minutes)
        reason = None
        if cursor < now:
            reason = "Đã qua"
        else:
            for maintenance in court.maintenance_windows:
                # Use UTC for safe timezone comparisons including SQLite tests.
                if ensure_utc(cursor) < ensure_utc(maintenance.end_at) and ensure_utc(end) > ensure_utc(maintenance.start_at):
                    reason = "Bảo trì / Tạm đóng"
                    break
        if reason is None:
            for allocation in occupied:
                if ensure_utc(cursor) < ensure_utc(allocation.end_at) and ensure_utc(end) + timedelta(minutes=court.buffer_minutes) > ensure_utc(allocation.start_at):
                    reason = "Đã đặt / Lịch thi đấu"
                    break
        slots.append(SlotOut(start_at=cursor, end_at=end, available=reason is None, reason=reason))
        cursor += timedelta(minutes=30)
    return AvailabilityOut(court_id=court_id, date=date, duration_minutes=minutes, slots=slots)
