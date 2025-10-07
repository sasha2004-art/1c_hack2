from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional # Импортируем Optional

from .. import crud, schemas, models
from ..db.base import get_db
from ..dependencies import get_current_active_user # Импортируем get_current_active_user

router = APIRouter()

@router.get("/lists/{public_key}", response_model=schemas.ListPublicRead)
def read_public_list(
    public_key: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_active_user) # Делаем пользователя необязательным
):
    """
    Получение публичного списка по его уникальному ключу.
    Не требует аутентификации.
    """
    db_list = crud.get_list_by_public_key(db, public_key=public_key)
    
    if db_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    
    # Проверяем, что список действительно публичный
    if db_list.privacy_level != models.PrivacyLevel.PUBLIC:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This list is not public")

    # Если текущий пользователь - владелец списка, скрываем информацию о бронированиях
    if current_user and db_list.owner_id == current_user.id:
        for item in db_list.items:
            item.is_reserved = False # Владелец не видит, что его предметы забронированы
    else:
        # Для гостей и других пользователей показываем, забронирован ли предмет
        for item in db_list.items:
            reservation = crud.get_reservation_by_item_id(db, item_id=item.id)
            item.is_reserved = bool(reservation) # True, если есть бронирование, False иначе
        
    return db_list

@router.get("/feed", response_model=list[schemas.ListPublicRead])
def read_public_lists_feed(
    db: Session = Depends(get_db)
):
    """
    Получение всех публичных списков для ленты.
    Не требует аутентификации.
    """
    public_lists = crud.get_public_lists(db)
    return public_lists