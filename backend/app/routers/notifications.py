# backend/app/routers/notifications.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List # <--- Убедитесь, что List импортирован

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

@router.get("/", response_model=schemas.NotificationsResponse)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получить уведомления текущего пользователя и количество непрочитанных."""
    db_notifications = crud.get_notifications_for_user(db, user_id=current_user.id)
    unread_count = crud.count_unread_notifications(db, user_id=current_user.id)
    
    # --- НАЧАЛО ИЗМЕНЕНИЙ ---
    # Вручную создаем список ответов, чтобы добавить вложенные данные
    response_notifications: List[schemas.NotificationRead] = []
    for notification in db_notifications:
        list_id = None
        # Если есть связанный элемент, получаем ID его списка
        if notification.related_item:
            list_id = notification.related_item.list_id

        response_notifications.append(
            schemas.NotificationRead(
                id=notification.id,
                is_read=notification.is_read,
                type=notification.type,
                created_at=notification.created_at,
                sender=notification.sender,
                related_item_id=notification.related_item_id,
                related_list_id=list_id # <--- Передаем ID списка
            )
        )
    # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    return {"unread_count": unread_count, "notifications": response_notifications}

@router.post("/{notification_id}/read", response_model=schemas.NotificationRead)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Пометить конкретное уведомление как прочитанное."""
    updated_notification = crud.mark_notification_as_read(db, notification_id=notification_id, user_id=current_user.id)
    if not updated_notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found or already read")
    return updated_notification