from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.db.session import get_db
from app.models import Sport, UserRole
from app.schemas import SportIn, SportOut, SportPatch

router = APIRouter(prefix="/sports", tags=["Sports"])


@router.get("", response_model=list[SportOut])
def list_sports(db: Session = Depends(get_db)):
    return db.scalars(select(Sport).where(Sport.active.is_(True)).order_by(Sport.name)).all()


@router.get("/admin", response_model=list[SportOut])
def list_all_sports(
    db: Session = Depends(get_db),
    _admin=Depends(require_roles(UserRole.ADMIN)),
):
    return db.scalars(select(Sport).order_by(Sport.name)).all()


@router.post("", response_model=SportOut, status_code=201)
def create_sport(body: SportIn, db: Session = Depends(get_db), _admin=Depends(require_roles(UserRole.ADMIN))):
    sport = Sport(name=body.name.strip(), active=body.active)
    db.add(sport)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Môn thể thao đã tồn tại") from exc
    db.refresh(sport)
    return sport


@router.patch("/{sport_id}", response_model=SportOut)
def update_sport(sport_id: int, body: SportPatch, db: Session = Depends(get_db), _admin=Depends(require_roles(UserRole.ADMIN))):
    sport = db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(404, "Không tìm thấy môn thể thao")
    for k, v in body.model_dump(exclude_unset=True).items():
        if v is None:
            raise HTTPException(422, "Trường cập nhật không thể null")
        setattr(sport, k, v.strip() if k == "name" else v)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Tên môn thể thao bị trùng") from exc
    db.refresh(sport)
    return sport
