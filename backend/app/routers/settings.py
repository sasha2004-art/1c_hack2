# backend/app/routers/settings.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas, security
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_user_password(
    password_data: schemas.PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Изменение пароля текущего пользователя."""
    # 1. Проверить, что текущий пароль верный
    if not security.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный текущий пароль")

    # 2. Обновить пароль
    crud.update_user_password(db=db, db_user=current_user, new_password=password_data.new_password)
    return


@router.put("/email", response_model=schemas.UserRead)
def change_user_email(
    email_data: schemas.EmailUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Изменение email текущего пользователя."""
    # 1. Проверить пароль
    if not security.verify_password(email_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный пароль")

    # 2. Проверить, не занят ли новый email
    existing_user = crud.get_user_by_email(db, email=email_data.new_email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Этот email уже используется")

    # 3. Обновить email
    return crud.update_user_email(db=db, db_user=current_user, new_email=email_data.new_email)


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(
    password_container: dict, # Просто получаем пароль в теле запроса
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Удаление аккаунта текущего пользователя."""
    password = password_container.get("password")
    if not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Пароль не предоставлен")
         
    # 1. Проверить пароль для подтверждения
    if not security.verify_password(password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Неверный пароль")
    
    # 2. Удалить пользователя
    crud.delete_user(db=db, db_user=current_user)
    return