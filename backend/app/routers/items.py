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
    
    # ---> ДОБАВЬТЕ ЭТОТ БЛОК ПРОВЕРКИ <---
    if item_data.goal_settings and db_list.list_type != models.ListType.TODO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Цели с отслеживанием прогресса доступны только для 'Списков дел'."
        )
    # ---> КОНЕЦ БЛОКА ПРОВЕРКИ <---
    
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