"""Local Sprint 2 demo data, based on the Fullstack prototype dataset."""
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo
from sqlalchemy import select
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import User, UserRole, Sport, Court, OperatingHour, Booking, Payment, CourtAllocation, Notification, MaintenanceWindow

VN = ZoneInfo('Asia/Ho_Chi_Minh')
USERS = [('owner','Nguyễn Văn Minh',UserRole.OWNER),('owner2','Trần Thu Hà',UserRole.OWNER),('player','Lê Quang Nam',UserRole.PLAYER),('player2','Ngô Thùy Linh',UserRole.PLAYER),('player3','Phạm Hoàng Anh',UserRole.PLAYER),('organizer','Hoàng Gia Bảo',UserRole.ORGANIZER),('admin','Quản trị hệ thống',UserRole.ADMIN)]
COURTS = [
 ('Sân bóng Minh Khai','Bóng đá','Hai Bà Trưng','120 Minh Khai, Hà Nội',250000),
 ('Cầu lông Hoàng Mai','Cầu lông','Hoàng Mai','36 Giải Phóng, Hà Nội',100000),
 ('Tennis Tây Hồ','Tennis','Tây Hồ','18 Xuân Diệu, Hà Nội',320000),
 ('Pickleball Cầu Giấy','Pickleball','Cầu Giấy','55 Trần Duy Hưng, Hà Nội',180000),
 ('Sân bóng Mỹ Đình','Bóng đá','Nam Từ Liêm','6 Lê Đức Thọ, Hà Nội',390000),
 ('Cầu lông Trần Duy Hưng','Cầu lông','Cầu Giấy','90 Trần Duy Hưng, Hà Nội',120000),
 ('Sân bóng rổ Bách Khoa','Bóng rổ','Hai Bà Trưng','1 Đại Cồ Việt, Hà Nội',210000),
 ('Tennis Nguyễn Chí Thanh','Tennis','Đống Đa','79 Nguyễn Chí Thanh, Hà Nội',300000),
 ('Pickleball Long Biên','Pickleball','Long Biên','12 Nguyễn Văn Cừ, Hà Nội',175000),
 ('Sân bóng Thanh Xuân','Bóng đá','Thanh Xuân','98 Nguyễn Trãi, Hà Nội',280000),
 ('Bóng chuyền Nghĩa Tân','Bóng chuyền','Cầu Giấy','27 Nghĩa Tân, Hà Nội',160000),
 ('Cầu lông Hà Đông','Cầu lông','Hà Đông','25 Trần Phú, Hà Nội',90000),
]

def local_dt(days, hour):
    return datetime.combine(datetime.now(VN).date()+timedelta(days=days),time(hour),VN).astimezone(timezone.utc)

def seed_demo():
    if settings.app_env != 'development' or not settings.seed_demo_data:
        return
    with SessionLocal() as db:
        users={}
        for key,name,role in USERS:
            email=f'{key}@demo.example.com'
            user=db.scalar(select(User).where(User.email==email))
            if user is None:
                user=User(email=email,full_name=name,role=role,password_hash=hash_password('Demo123!'))
                db.add(user)
            users[key]=user
        sports={}
        for name in sorted({c[1] for c in COURTS}):
            row=db.scalar(select(Sport).where(Sport.name==name))
            if row is None:
                row=Sport(name=name); db.add(row)
            sports[name]=row
        db.flush()
        new_courts={}
        for i,(name,sport,district,address,price) in enumerate(COURTS):
            court=db.scalar(select(Court).where(Court.name==name))
            if court is None:
                court=Court(name=name,owner_id=users['owner' if i<6 else 'owner2'].id,sport_id=sports[sport].id,district=district,address=address,price_per_hour=Decimal(price),min_duration_minutes=60,buffer_minutes=0,description=f'Sân {sport.lower()} tại {district}. Dữ liệu minh họa.')
                court.operating_hours=[OperatingHour(weekday=d,open_time=time(6),close_time=time(22)) for d in range(7)]
                db.add(court);new_courts[name]=court
        db.flush()
        # Only seed occupancy on newly created courts; never overwrite existing reservations.
        cases=[(0,'player',1,18,'CONFIRMED','UNPAID'),(0,'player2',1,19,'PENDING','UNPAID'),(1,'player',2,18,'CONFIRMED','SUBMITTED'),(3,'player2',2,19,'CONFIRMED','PAID'),(2,'player',3,17,'PENDING','UNPAID'),(4,'player2',4,19,'CONFIRMED','PAID'),(6,'player',5,18,'CONFIRMED','PAID'),(5,'player2',6,19,'PENDING','UNPAID')]
        for i,key,day,h,status,payment in cases:
            c=new_courts.get(COURTS[i][0])
            if c is None: continue
            start,end=local_dt(day,h),local_dt(day,h+1)
            b=Booking(court_id=c.id,player_id=users[key].id,start_at=start,end_at=end,status=status,total_amount=c.price_per_hour,note='Dữ liệu mẫu để demo.')
            db.add(b);db.flush()
            db.add(CourtAllocation(court_id=c.id,booking_id=b.id,start_at=start,end_at=end,active=True))
            db.add(Payment(booking_id=b.id,amount=b.total_amount,status=payment,reference='' if payment=='UNPAID' else f'DEMO-{b.id}'))
        if COURTS[0][0] in new_courts:
            db.add(MaintenanceWindow(court_id=new_courts[COURTS[0][0]].id,start_at=local_dt(1,10),end_at=local_dt(1,12),reason='Bảo trì demo'))
        for user in users.values():
            if db.scalar(select(Notification.id).where(Notification.user_id==user.id,Notification.title=='Chào mừng đến DatSân')) is None:
                db.add(Notification(user_id=user.id,title='Chào mừng đến DatSân',message='Tài khoản demo sẵn sàng. Thanh toán chỉ là mô phỏng.'))
        db.commit()
    print('Sprint 2 development seed completed.')

if __name__=='__main__':
    seed_demo()
