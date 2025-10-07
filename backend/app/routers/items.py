from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import os
from PIL import Image

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter()

@router.post("/lists/{list_id}/items", response_model=schemas.ItemRead, status_code=status.HTTP_201_CREATED)
def create_item_for_list(
    list_id: int,
    item_data: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Создание нового элемента в конкретном списке."""
    db_list = crud.get_list(db, list_id=list_id)
    if not db_list:
        raise HTTPException(status_code=404, detail="Список не найден")
    if db_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    return crud.create_list_item(db=db, item_data=item_data, list_id=list_id)

@router.put("/items/{item_id}", response_model=schemas.ItemRead)
def update_item(
    item_id: int,
    item_data: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Обновление элемента по его ID."""
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    
    # Проверяем, что пользователь является владельцем списка, к которому относится элемент
    if db_item.list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
        
    return crud.update_item(db=db, db_item=db_item, item_data=item_data)

@router.delete("/items/{item_id}", response_model=schemas.ItemRead)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Удаление элемента по его ID."""
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    
    # Проверяем, что пользователь является владельцем списка
    if db_item.list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
        
    return crud.delete_item(db=db, db_item=db_item)

@router.post("/items/{item_id}/upload-image", response_model=schemas.ItemRead)
def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Загрузка изображения для элемента и генерация миниатюры."""
    db_item = crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Элемент не найден")
    
    # Проверяем, что пользователь является владельцем списка
    if db_item.list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Создаем папки если не существуют
    originals_dir = "static/uploads/originals"
    thumbnails_dir = "static/uploads/thumbnails"
    os.makedirs(originals_dir, exist_ok=True)
    os.makedirs(thumbnails_dir, exist_ok=True)
    
    # Сохраняем оригинальное изображение
    original_path = f"{originals_dir}/{item_id}_{file.filename}"
    with open(original_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    # Генерируем миниатюру
    image = Image.open(original_path)
    image.thumbnail((300, 300))  # Размер миниатюры 300x300
    thumbnail_path = f"{thumbnails_dir}/{item_id}_thumb_{file.filename}"
    image.save(thumbnail_path)
    
    # Обновляем элемент в базе данных
    item_data = schemas.ItemUpdate(
        image_url=f"/{original_path}",
        thumbnail_url=f"/{thumbnail_path}"
    )
    updated_item = crud.update_item(db=db, db_item=db_item, item_data=item_data)
    
    return updated_item

@router.post("/items/{item_id}/copy", response_model=schemas.ItemRead, status_code=status.HTTP_201_CREATED)
def copy_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Копирование элемента из чужого списка в свой список по умолчанию (или создание нового)."""
    source_item = crud.get_item(db, item_id=item_id)
    if not source_item:
        raise HTTPException(status_code=404, detail="Исходный элемент не найден")

    # Нельзя скопировать элемент из своего же списка
    if source_item.list.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя скопировать элемент из своего же списка")

    # Получаем или создаем список по умолчанию для пользователя
    # В данном случае, просто возьмем первый попавшийся список пользователя
    # В реальном приложении, возможно, нужно создать специальный список "Мои сохранения" или "Избранное"
    user_lists = crud.get_lists_by_user(db, user_id=current_user.id)
    if not user_lists:
        # Если у пользователя нет списков, создаем новый список "Мои элементы"
        new_list_data = schemas.ListCreate(
            title="Мои сохраненные элементы",
            description="Элементы, скопированные из других списков",
            list_type=models.ListType.WISHLIST, # Используем WISHLIST как тип по умолчанию
            privacy_level=models.PrivacyLevel.PRIVATE # Приватный по умолчанию
        )
        target_list = crud.create_user_list(db=db, list_data=new_list_data, user_id=current_user.id)
    else:
        target_list = user_lists[0] # Используем первый попавшийся список пользователя
    
    copied_item = crud.copy_item_to_list(db=db, source_item=source_item, target_list_id=target_list.id)
    
    return copied_item