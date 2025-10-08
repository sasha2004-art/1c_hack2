# backend/app/routers/lists.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter()

# Вспомогательная функция для сборки ответа
def assemble_list_response(db_list: models.List, current_user_id: int) -> schemas.ListRead:
    items_response = []
    for item in db_list.items:
        likes_count = len(item.likes)
        is_liked = any(like.user_id == current_user_id for like in item.likes)
        
        item_data = schemas.ItemRead(
            id=item.id,
            list_id=item.list_id,
            title=item.title,
            description=item.description,
            image_url=item.image_url, # <-- ДОБАВЛЕНО НА ВСЯКИЙ СЛУЧАЙ, ЕСЛИ ПРОПУСТИЛИ
            thumbnail_url=item.thumbnail_url, # <-- ДОБАВЛЕНО НА ВСЯКИЙ СЛУЧАЙ, ЕСЛИ ПРОПУСТИЛИ
            is_completed=item.is_completed, # <--- ВОТ ИСПРАВЛЕНИЕ!
            created_at=item.created_at,
            updated_at=item.updated_at,
            likes_count=likes_count,
            is_liked_by_current_user=is_liked,
            comments=[schemas.CommentRead.from_orm(c) for c in item.comments],
            goal_tracker=item.goal_tracker # <-- ДОБАВЛЕНО ДЛЯ ПОЛНОТЫ
        )
        items_response.append(item_data)
    
    return schemas.ListRead(
        id=db_list.id,
        owner_id=db_list.owner_id,
        public_url_key=db_list.public_url_key,
        title=db_list.title,
        description=db_list.description,
        list_type=db_list.list_type,
        privacy_level=db_list.privacy_level,
        theme_name=db_list.theme_name,
        created_at=db_list.created_at,
        updated_at=db_list.updated_at,
        items=items_response
    )

@router.post("/", response_model=schemas.ListRead, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: schemas.ListCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Создание нового списка для текущего пользователя."""
    db_list = crud.create_user_list(db=db, list_data=list_data, user_id=current_user.id)
    # Возвращаем через assemble_list_response, чтобы сразу были все поля
    return assemble_list_response(db_list, current_user.id)


@router.get("/", response_model=List[schemas.ListRead])
def read_user_lists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получение всех списков текущего пользователя."""
    lists = crud.get_lists_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    # Прогоняем каждый список через сборщик, чтобы обеспечить консистентность данных
    return [assemble_list_response(l, current_user.id) for l in lists]


@router.get("/{list_id}", response_model=schemas.ListRead)
def read_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получение одного списка по ID."""
    db_list = crud.get_list(db, list_id=list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    
    # --- (Задача 6.1) Новая логика проверки доступа ---
    is_owner = db_list.owner_id == current_user.id
    
    if is_owner:
        return assemble_list_response(db_list, current_user.id)

    if db_list.privacy_level == models.PrivacyLevel.PRIVATE:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if db_list.privacy_level == models.PrivacyLevel.FRIENDS_ONLY:
        are_friends = crud.are_users_friends(db, user1_id=current_user.id, user2_id=db_list.owner_id)
        if not are_friends:
            raise HTTPException(status_code=403, detail="This list is only available to friends.")

    # Если дошли сюда, значит список публичный или для друзей (и мы друг)
    return assemble_list_response(db_list, current_user.id)


@router.put("/{list_id}", response_model=schemas.ListRead)
def update_list(
    list_id: int,
    list_data: schemas.ListUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Обновление списка."""
    db_list = crud.get_list(db, list_id=list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    if db_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_list = crud.update_list(db=db, db_list=db_list, list_data=list_data)
    # Возвращаем обновленные данные с лайками и комментами
    return assemble_list_response(updated_list, current_user.id)


@router.delete("/{list_id}", response_model=schemas.ListRead)
def delete_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Удаление списка."""
    db_list = crud.get_list(db, list_id=list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    if db_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    response_data = assemble_list_response(db_list, current_user.id)
    crud.delete_list(db=db, db_list=db_list)
    return response_data