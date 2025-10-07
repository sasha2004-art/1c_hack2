from sqlalchemy.orm import Session
from typing import List as TypingList, Optional
from uuid import UUID # Импортируем UUID
from . import models, schemas, security

# --- CRUD для Пользователей ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- CRUD для Списков ---

def get_list(db: Session, list_id: int) -> Optional[models.List]:
    """Получить один список по его ID."""
    return db.query(models.List).filter(models.List.id == list_id).first()

# Новая функция для получения списка по публичному ключу
def get_list_by_public_key(db: Session, public_key: UUID) -> Optional[models.List]:
    """Получить один список по его публичному UUID ключу."""
    return db.query(models.List).filter(models.List.public_url_key == public_key).first()

def get_lists_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> TypingList[models.List]:
    """Получить все списки конкретного пользователя."""
    return db.query(models.List).filter(models.List.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_list(db: Session, list_data: schemas.ListCreate, user_id: int) -> models.List:
    """Создать новый список для пользователя."""
    db_list = models.List(**list_data.dict(), owner_id=user_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

def update_list(db: Session, db_list: models.List, list_data: schemas.ListUpdate) -> models.List:
    """Обновить существующий список."""
    update_data = list_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_list, key, value)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

def delete_list(db: Session, db_list: models.List):
    """Удалить список."""
    db.delete(db_list)
    db.commit()
    return db_list

# --- CRUD для Элементов ---

def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    """Получить один элемент по его ID."""
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def create_list_item(db: Session, item_data: schemas.ItemCreate, list_id: int) -> models.Item:
    """Создать новый элемент в списке."""
    db_item = models.Item(**item_data.dict(), list_id=list_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, db_item: models.Item, item_data: schemas.ItemUpdate) -> models.Item:
    """Обновить существующий элемент."""
    update_data = item_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, db_item: models.Item):
    """Удалить элемент."""
    db.delete(db_item)
    db.commit()
    return db_item
