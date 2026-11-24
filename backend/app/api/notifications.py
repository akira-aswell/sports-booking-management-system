from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.models import Notification,User
from app.schemas import NotificationOut

router=APIRouter(prefix='/notifications', tags=['Notifications'])

@router.get('',response_model=list[NotificationOut])
def list_notifications(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return db.scalars(select(Notification).where(Notification.user_id==user.id).order_by(Notification.created_at.desc()).limit(100)).all()

@router.post('/{notification_id}/read',response_model=NotificationOut)
def mark_read(notification_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    row=db.get(Notification,notification_id)
    if not row or row.user_id!=user.id:
        raise HTTPException(404,'Không tìm thấy thông báo')
    row.read=True;db.commit();return row
