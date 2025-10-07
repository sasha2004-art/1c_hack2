from fastapi import APIRouter, Depends, HTTPException, status
from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from sqlalchemy.orm import Session
from ..db.base import get_db

router = APIRouter()

@router.get("/me", response_model=schemas.UserRead)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=schemas.UserRead)
def update_users_me(
    user_update: schemas.UserUpdate, 
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли никнейм, если он передан и отличается от текущего
    if user_update.nickname and user_update.nickname != current_user.nickname:
        existing_user = crud.get_user_by_nickname(db, nickname=user_update.nickname)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname already registered")

    updated_user = crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user
