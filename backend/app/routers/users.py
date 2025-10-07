from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from .. import schemas, models, crud
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter()

@router.get("/me", response_model=schemas.UserRead)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@router.get("/me/reservations", response_model=List[schemas.ReservationRead])
def read_my_reservations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получить все элементы, забронированные текущим пользователем."""
    return crud.get_reservations_by_user(db=db, user_id=current_user.id)
