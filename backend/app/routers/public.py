from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

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
    
    # Проверяем, что список действительно публичный
    if db_list.privacy_level != models.PrivacyLevel.PUBLIC:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This list is not public")
        
    return db_list

@router.get("/feed", response_model=list[schemas.ListPublicRead])
def read_public_lists_feed(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение всех публичных списков для ленты.
    Не требует аутентификации.
    """
    public_lists = crud.get_public_lists(db, skip=skip, limit=limit)
    return public_lists