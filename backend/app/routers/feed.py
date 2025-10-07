# backend/app/routers/feed.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter()

@router.get("/friends-lists", response_model=List[schemas.ListForFeedRead])
def get_friends_feed(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Получает ленту списков от друзей пользователя с пагинацией.
    """
    db_lists = crud.get_friends_feed_lists(db, user_id=current_user.id, skip=skip, limit=limit)
    
    # Вручную конструируем ответ, чтобы включить items_count
    response_lists = []
    for db_list in db_lists:
        list_data = schemas.ListForFeedRead(
            id=db_list.id,
            public_url_key=db_list.public_url_key, # <--- ДОБАВЛЕНО ПОЛЕ
            title=db_list.title,
            description=db_list.description,
            list_type=db_list.list_type,
            privacy_level=db_list.privacy_level,
            theme_name=db_list.theme_name,
            owner=db_list.owner,
            created_at=db_list.created_at,
            items_count=len(db_list.items)
        )
        response_lists.append(list_data)

    return response_lists