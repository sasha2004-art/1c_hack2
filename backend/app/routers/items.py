from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

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