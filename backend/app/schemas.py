from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from .models import ListType, PrivacyLevel

# --- Схемы для пользователя ---

class UserBase(BaseModel):
    """Базовая схема для пользователя с общими полями."""
    email: EmailStr

class UserCreate(UserBase):
    """Схема для создания нового пользователя. Требует пароль."""
    password: str

class UserRead(UserBase):
    """Схема для чтения (возврата) данных о пользователе из API."""
    id: int
    is_active: bool

    class Config:
        # Разрешает Pydantic читать данные из атрибутов объекта SQLAlchemy
        from_attributes = True

# --- Схемы для элементов списка ---

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ItemRead(ItemBase):
    id: int
    list_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
# --- Схемы для списков ---

class ListBase(BaseModel):
    title: str
    description: Optional[str] = None
    list_type: ListType = ListType.WISHLIST
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE

class ListCreate(ListBase):
    pass

class ListUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    list_type: Optional[ListType] = None
    privacy_level: Optional[PrivacyLevel] = None

class ListRead(ListBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Добавляем элементы в схему для чтения списка
    items: list[ItemRead] = []

    class Config:
        from_attributes = True