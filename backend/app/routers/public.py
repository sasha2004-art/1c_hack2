from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from .. import crud, schemas, models
from ..db.base import get_db
from ..dependencies import get_optional_current_user

# --- ИЗМЕНЕНИЕ ЗДЕСЬ: Убираем prefix="/public" ---
router = APIRouter(
    tags=["public"]
)

# --- ИЗМЕНЕНИЕ: Вся функция была обновлена для возврата структурированных ошибок ---
@router.get("/lists/{public_key}", response_model=schemas.ListPublicRead)
def read_public_list(
    public_key: UUID, 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user)
):
    """
    Получение публичного списка или списка для друзей по его уникальному ключу.
    Аутентификация опциональна.
    """
    db_list = crud.get_list_by_public_key(db, public_key=public_key)
    
    if db_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    
    is_public = db_list.privacy_level == models.PrivacyLevel.PUBLIC
    is_friends_only = db_list.privacy_level == models.PrivacyLevel.FRIENDS_ONLY

    # --- ИСПРАВЛЕННАЯ И БОЛЕЕ НАДЕЖНАЯ ЛОГИКА ПРОВЕРКИ ДОСТУПА ---
    
    if is_public:
        # Публичные списки доступны всем
        pass
    elif is_friends_only:
        # Списки для друзей требуют проверки
        if not current_user:
            # Если пользователь не залогинен - ошибка 401 с данными владельца
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Authentication required to view this friends-only list.",
                    "owner": schemas.UserInComment.from_orm(db_list.owner)
                }
            )
        
        is_owner = current_user.id == db_list.owner_id
        # Проверяем дружбу только если текущий пользователь НЕ является владельцем
        if not is_owner:
            are_friends = crud.are_users_friends(db, user1_id=current_user.id, user2_id=db_list.owner_id)
            if not are_friends:
                # Если они не друзья - ошибка 403 с данными владельца
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": "This list is only available to friends.",
                        "owner": schemas.UserInComment.from_orm(db_list.owner)
                    }
                )
    else:
        # Приватные списки недоступны по ссылке
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "This list is private and cannot be viewed via a link."}
        )
        
    # Создаем ответ вручную, чтобы добавить поле is_reserved
    items_with_extra_data = []
    for item in db_list.items:
        reservation = crud.get_reservation_by_item_id(db, item_id=item.id)
        
        item_data = schemas.ItemPublicRead(
            id=item.id,
            title=item.title,
            description=item.description,
            is_reserved=reservation is not None,
            likes_count=len(item.likes),
            comments=[schemas.CommentRead.from_orm(c) for c in item.comments]
        )
        items_with_extra_data.append(item_data)
        
    # Собираем финальный объект ответа
    public_list_data = schemas.ListPublicRead(
        id=db_list.id,
        owner=db_list.owner,
        title=db_list.title,
        description=db_list.description,
        list_type=db_list.list_type,
        privacy_level=db_list.privacy_level,
        theme_name=db_list.theme_name,
        items=items_with_extra_data
    )
        
    return public_list_data