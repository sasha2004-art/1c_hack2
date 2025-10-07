from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter()

@router.get("/friends-lists", response_model=List[schemas.ListRead])
def get_friends_lists(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получить агрегированные списки от друзей пользователя."""
    # Получаем списки друзей с учетом пагинации
    friends_lists = crud.get_friends_lists_for_feed(
        db=db,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return friends_lists
