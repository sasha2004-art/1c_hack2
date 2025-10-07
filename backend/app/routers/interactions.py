from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# --- ДОБАВИТЬ ИМПОРТЫ ---
from fastapi import BackgroundTasks
from ..ws_manager import send_notification_ws

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter(
    tags=["interactions"]
)

# --- Эндпоинты для Лайков ---

@router.post("/items/{item_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def like_item(
    item_id: int,
    background_tasks: BackgroundTasks, # <-- Внедряем
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Поставить лайк элементу."""
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    existing_like = crud.get_like(db, item_id=item_id, user_id=current_user.id)
    if existing_like:
        raise HTTPException(status_code=409, detail="Вы уже лайкнули этот элемент")

    # ИЗМЕНЕНИЕ: add_like теперь возвращает объект
    db_like = crud.add_like(db=db, item=db_item, user=current_user)
    if db_like.item.list.owner_id != current_user.id:
        # Находим уведомление
        notification = db_like.item.list.owner.notifications[-1]
        background_tasks.add_task(send_notification_ws, notification)
    return

@router.delete("/items/{item_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Убрать лайк с элемента."""
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    like_to_delete = crud.get_like(db, item_id=item_id, user_id=current_user.id)
    if not like_to_delete:
        raise HTTPException(status_code=404, detail="Лайк не найден")

    crud.remove_like(db=db, db_like=like_to_delete)
    return

# --- Эндпоинты для Комментариев ---

@router.post("/items/{item_id}/comments", response_model=schemas.CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment_for_item(
    item_id: int,
    comment_data: schemas.CommentCreate,
    background_tasks: BackgroundTasks, # <-- Внедряем
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Добавить комментарий к элементу."""
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")

    # ИЗМЕНЕНИЕ: create_comment теперь возвращает объект
    db_comment = crud.create_comment(db=db, comment_data=comment_data, item_id=item_id, user_id=current_user.id)
    if db_comment.item.list.owner_id != current_user.id:
        notification = db_comment.item.list.owner.notifications[-1]
        background_tasks.add_task(send_notification_ws, notification)
    return db_comment


@router.delete("/comments/{comment_id}", response_model=schemas.CommentRead)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Удалить свой комментарий."""
    db_comment = crud.get_comment(db, comment_id=comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    
    # Проверяем, что пользователь является владельцем комментария
    if db_comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для удаления этого комментария")

    return crud.delete_comment(db=db, db_comment=db_comment)