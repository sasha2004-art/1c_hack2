from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session

from .. import schemas, models, crud
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter()

@router.get("/me", response_model=schemas.UserRead)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

# --- ИЗМЕНИТЬ ЭТУ ФУНКЦИЮ ---
@router.get("/search", response_model=List[schemas.UserInComment])
def search_users(
    query: Optional[str] = "", # Переименовываем 'email' в 'query'
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Поиск пользователей по email или имени."""
    if not query:
        return []
    # Вызываем обновленную CRUD функцию
    users = crud.search_users_by_email(db, query=query, current_user_id=current_user.id)
    return users

# (Задача 3.2) Новый эндпоинт для профиля
@router.get("/{user_id}/profile", response_model=schemas.UserProfileResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получить публичный профиль пользователя."""
    profile_user = crud.get_user(db, user_id=user_id)
    if not profile_user:
        raise HTTPException(status_code=404, detail="User not found")

    # ---- ИЗМЕНЕНИЕ ЗДЕСЬ ----
    # Вызываем новую, более умную функцию вместо get_public_lists_by_user
    visible_lists = crud.get_visible_lists_by_user(
        db, 
        profile_owner_id=user_id, 
        viewer_id=current_user.id
    )
    
    status = "none"
    friendship_id = None
    
    if user_id != current_user.id:
        friendship = crud.get_existing_friendship(db, user1_id=current_user.id, user2_id=user_id)
        if friendship:
            friendship_id = friendship.id
            if friendship.status == models.FriendshipStatus.ACCEPTED:
                status = "friends"
            elif friendship.status == models.FriendshipStatus.PENDING:
                if friendship.requester_id == current_user.id:
                    status = "request_sent"
                else:
                    status = "request_received"

    return schemas.UserProfileResponse(
        user_info=schemas.UserInComment.from_orm(profile_user),
        public_lists=visible_lists, # <--- Передаем результат новой функции
        friendship_status=status,
        friendship_id=friendship_id
    )

@router.get("/me/reservations", response_model=List[schemas.ReservationRead])
def read_my_reservations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получить все элементы, забронированные текущим пользователем."""
    return crud.get_reservations_by_user(db=db, user_id=current_user.id)
