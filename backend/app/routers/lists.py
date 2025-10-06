from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models
from ..dependencies import get_current_active_user
from ..db.base import get_db

router = APIRouter()

@router.post("/", response_model=schemas.ListRead, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: schemas.ListCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Создание нового списка для текущего пользователя."""
    return crud.create_user_list(db=db, list_data=list_data, user_id=current_user.id)


@router.get("/", response_model=List[schemas.ListRead])
def read_user_lists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Получение всех списков текущего пользователя."""
    lists = crud.get_lists_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return lists


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
    if db_list.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_list


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
    return crud.update_list(db=db, db_list=db_list, list_data=list_data)


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
    return crud.delete_list(db=db, db_list=db_list)