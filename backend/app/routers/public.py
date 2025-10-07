from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from .. import crud, schemas, models
from ..db.base import get_db

router = APIRouter()

@router.get("/lists/{public_key}", response_model=schemas.ListPublicRead)
def read_public_list(public_key: UUID, db: Session = Depends(get_db)):
    """
    Получение публичного списка по его уникальному ключу.
    Не требует аутентификации.
    """
    db_list = crud.get_list_by_public_key(db, public_key=public_key)
    
    if db_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    
    if db_list.privacy_level != models.PrivacyLevel.PUBLIC:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This list is not public")
        
    # Создаем ответ вручную, чтобы добавить поле is_reserved
    items_with_reservation_status = []
    for item in db_list.items:
        reservation = crud.get_reservation_by_item_id(db, item_id=item.id)
        item_data = schemas.ItemPublicRead.from_orm(item)
        item_data.is_reserved = reservation is not None
        items_with_reservation_status.append(item_data)
        
    # Собираем финальный объект ответа
    public_list_data = schemas.ListPublicRead(
        id=db_list.id,
        title=db_list.title,
        description=db_list.description,
        list_type=db_list.list_type,
        privacy_level=db_list.privacy_level,
        theme_name=db_list.theme_name,
        items=items_with_reservation_status
    )
        
    return public_list_data