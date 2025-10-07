from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import crud
from ..routers import lists as crud_lists
from .. import schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter(
    prefix="/feed",
    tags=["feed"]
)

@router.get("/friends-lists", response_model=List[schemas.ListRead])
def get_friends_feed(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Получить ленту списков от друзей.
    Включает публичные списки и списки "только для друзей".
    Отсортировано по дате создания (сначала новые).
    """
    feed_lists = crud.get_friends_feed(db=db, user_id=current_user.id, skip=skip, limit=limit)
    response = []
    for db_list in feed_lists:
        list_response = crud_lists.assemble_list_response(db_list, current_user.id)
        response.append(list_response)
    return response
