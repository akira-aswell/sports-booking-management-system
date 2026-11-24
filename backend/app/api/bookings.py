from datetime import timedelta, datetime, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user, require_roles
from app.db.session import get_db
from app.models import Booking, Payment, CourtAllocation, Court, User, UserRole
from app.schemas import BookingIn, BookingOut, RescheduleIn, PaymentSubmitIn
from app.api.courts import court_stmt
from app.services.scheduling import check_interval, fee, notify, conflict_from_db, utc, lock_court

router = APIRouter(prefix='/bookings', tags=['Bookings'])


def enrich(db: Session, b: Booking):
    pay = db.scalar(select(Payment).where(Payment.booking_id == b.id))
    return BookingOut.model_validate({
        'id': b.id, 'court_id': b.court_id, 'player_id': b.player_id,
        'start_at': utc(b.start_at), 'end_at': utc(b.end_at), 'status': b.status,
        'total_amount': b.total_amount, 'note': b.note, 'created_at': utc(b.created_at),
        'court_name': b.court.name, 'player_name': b.player.full_name,
        'payment_status': pay.status if pay else 'UNPAID',
    })


def booking_query():
    return select(Booking).options(selectinload(Booking.court),selectinload(Booking.player))


def access_booking(db: Session, booking_id: int, user: User, *, for_update: bool = False):
    if for_update:
        db.execute(select(Booking.id).where(Booking.id==booking_id).with_for_update()).scalar_one_or_none()
    b = db.scalar(booking_query().where(Booking.id == booking_id))
    if b is None:
        raise HTTPException(404,'Không tìm thấy đơn đặt sân')
    if user.role != UserRole.ADMIN and user.id not in (b.player_id, b.court.owner_id):
        raise HTTPException(403,'Bạn không có quyền xem đơn này')
    return b


@router.get('', response_model=list[BookingOut])
def list_bookings(scope: str = Query('mine', pattern='^(mine|owner|all)$'), db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    query = booking_query().order_by(Booking.start_at.desc()).limit(200)
    if scope == 'owner':
        if user.role not in (UserRole.OWNER,UserRole.ADMIN):
            raise HTTPException(403,'Chỉ chủ sân xem được danh sách đặt sân')
        if user.role != UserRole.ADMIN:
            query = query.join(Court).where(Court.owner_id == user.id)
    elif scope == 'all':
        if user.role != UserRole.ADMIN:
            raise HTTPException(403,'Chỉ Admin xem tất cả đơn đặt')
    else:
        query = query.where(Booking.player_id == user.id)
    return [enrich(db,b) for b in db.scalars(query).all()]


@router.post('', response_model=BookingOut, status_code=201)
def create_booking(body:BookingIn, db:Session=Depends(get_db), user:User=Depends(require_roles(UserRole.PLAYER, UserRole.ADMIN))):
    court = db.scalar(court_stmt().where(Court.id == body.court_id))
    if not court:
        raise HTTPException(404, 'Không tìm thấy sân')
    lock_court(db,court.id)
    start,end = check_interval(db,court,body.start_at,body.end_at)
    cost=fee(court,start,end)
    try:
        b=Booking(court_id=court.id,player_id=user.id,start_at=start,end_at=end,total_amount=cost,note=body.note,status='PENDING')
        db.add(b)
        db.flush()
        db.add(CourtAllocation(court_id=court.id,booking_id=b.id,start_at=start,end_at=end+timedelta(minutes=court.buffer_minutes),active=True))
        db.add(Payment(booking_id=b.id,amount=cost,status='UNPAID',method='DEMO_TRANSFER'))
        notify(db,court.owner_id,'Đơn đặt sân mới',f'{user.full_name} muốn đặt {court.name} vào {start.astimezone(__import__("zoneinfo").ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%d/%m %H:%M")}.')
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise conflict_from_db(e)
    return enrich(db,db.scalar(booking_query().where(Booking.id==b.id)))


@router.get('/{booking_id}',response_model=BookingOut)
def get_booking(booking_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return enrich(db,access_booking(db,booking_id,user))


@router.post('/{booking_id}/approve',response_model=BookingOut)
def approve_booking(booking_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles(UserRole.OWNER,UserRole.ADMIN))):
    b=access_booking(db,booking_id,user,for_update=True)
    if b.court.owner_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(403,'Chỉ chủ sân được duyệt')
    if b.status!='PENDING':
        raise HTTPException(409,'Chỉ duyệt đơn đang chờ')
    b.status='CONFIRMED'
    notify(db,b.player_id,'Đặt sân được duyệt',f'Đơn #{b.id} tại {b.court.name} đã được chủ sân chấp nhận.')
    db.commit()
    return enrich(db,b)


@router.post('/{booking_id}/reject',response_model=BookingOut)
def reject_booking(booking_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles(UserRole.OWNER,UserRole.ADMIN))):
    b=access_booking(db,booking_id,user,for_update=True)
    if b.court.owner_id!=user.id and user.role != UserRole.ADMIN:
        raise HTTPException(403,'Chỉ chủ sân được từ chối')
    if b.status!='PENDING':
        raise HTTPException(409,'Chỉ từ chối đơn đang chờ')
    b.status='REJECTED'
    allocation=db.scalar(select(CourtAllocation).where(CourtAllocation.booking_id==b.id))
    if allocation: allocation.active=False
    notify(db,b.player_id,'Đơn đặt sân bị từ chối',f'Đơn #{b.id} tại {b.court.name} bị từ chối.')
    db.commit()
    return enrich(db,b)


@router.post('/{booking_id}/cancel',response_model=BookingOut)
def cancel_booking(booking_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    b=access_booking(db,booking_id,user,for_update=True)
    if b.status not in ('PENDING','CONFIRMED'):
        raise HTTPException(409,'Không thể hủy đơn này')
    if utc(b.start_at) <= datetime.now(timezone.utc):
        raise HTTPException(409,'Không thể hủy khi trận đã bắt đầu')
    b.status='CANCELLED'
    allocation=db.scalar(select(CourtAllocation).where(CourtAllocation.booking_id==b.id))
    if allocation: allocation.active=False
    pay=db.scalar(select(Payment).where(Payment.booking_id==b.id))
    if pay and pay.status in ('PAID','SUBMITTED'): pay.status='REFUND_REVIEW'
    target=b.court.owner_id if user.id==b.player_id else b.player_id
    notify(db,target,'Đơn đặt sân đã hủy',f'Đơn #{b.id} tại {b.court.name} đã hủy. Nếu có thanh toán, cần xử lý hoàn tiền thủ công.')
    db.commit()
    return enrich(db,b)


@router.post('/{booking_id}/reschedule',response_model=BookingOut)
def reschedule_booking(booking_id:int,body:RescheduleIn,db:Session=Depends(get_db),user:User=Depends(require_roles(UserRole.PLAYER,UserRole.ADMIN))):
    b=access_booking(db,booking_id,user,for_update=True)
    if b.player_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(403,'Chỉ người đặt được đổi lịch')
    if b.status not in ('PENDING','CONFIRMED'):
        raise HTTPException(409,'Không thể đổi lịch đơn này')
    pay=db.scalar(select(Payment).where(Payment.booking_id==b.id))
    if pay and pay.status!='UNPAID':
        raise HTTPException(409,'Đã có yêu cầu thanh toán; cần liên hệ chủ sân để đổi lịch')
    alloc=db.scalar(select(CourtAllocation).where(CourtAllocation.booking_id==b.id))
    lock_court(db,b.court_id)
    start,end=check_interval(db,b.court,body.start_at,body.end_at,ignore_allocation_id=alloc.id)
    b.start_at=start;b.end_at=end;b.total_amount=fee(b.court,start,end);b.status='PENDING'
    alloc.start_at=start;alloc.end_at=end+timedelta(minutes=b.court.buffer_minutes)
    pay.amount=b.total_amount
    notify(db,b.court.owner_id,'Yêu cầu đổi lịch',f'Đơn #{b.id} đã đổi khung giờ, cần duyệt lại.')
    try: db.commit()
    except IntegrityError as e:
        db.rollback();raise conflict_from_db(e)
    return enrich(db,b)


@router.post('/{booking_id}/payment-submit',response_model=BookingOut)
def submit_demo_payment(booking_id:int,body:PaymentSubmitIn,db:Session=Depends(get_db),user:User=Depends(require_roles(UserRole.PLAYER,UserRole.ADMIN))):
    b=access_booking(db,booking_id,user,for_update=True)
    if b.player_id!=user.id and user.role!=UserRole.ADMIN:
        raise HTTPException(403,'Chỉ người đặt được khai báo thanh toán')
    if b.status!='CONFIRMED':
        raise HTTPException(409,'Đơn chưa được chủ sân duyệt')
    pay=db.scalar(select(Payment).where(Payment.booking_id==b.id))
    if pay.status not in ('UNPAID','SUBMITTED'):
        raise HTTPException(409,'Thanh toán không ở trạng thái hợp lệ')
    pay.status='SUBMITTED';pay.reference=body.reference;pay.updated_at=datetime.now(timezone.utc)
    notify(db,b.court.owner_id,'Chờ xác minh thanh toán',f'Đơn #{b.id} khai báo chuyển khoản mã {body.reference}. Đây là mô phỏng, chưa kiểm tra tiền thật.')
    db.commit()
    return enrich(db,b)


@router.post('/{booking_id}/payment-confirm',response_model=BookingOut)
def confirm_demo_payment(booking_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles(UserRole.OWNER,UserRole.ADMIN))):
    b=access_booking(db,booking_id,user,for_update=True)
    if b.court.owner_id!=user.id and user.role!=UserRole.ADMIN:
        raise HTTPException(403,'Chỉ chủ sân xác nhận')
    pay=db.scalar(select(Payment).where(Payment.booking_id==b.id))
    if b.status!='CONFIRMED' or pay.status!='SUBMITTED':
        raise HTTPException(409,'Chỉ xác nhận được yêu cầu thanh toán của đơn đã duyệt')
    pay.status='PAID';pay.updated_at=datetime.now(timezone.utc)
    notify(db,b.player_id,'Đã xác nhận thanh toán (demo)',f'Chủ sân đã xác nhận thanh toán mô phỏng cho đơn #{b.id}.')
    db.commit()
    return enrich(db,b)
