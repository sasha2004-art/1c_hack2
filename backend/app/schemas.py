from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .models import ListType, PrivacyLevel, ThemeName

# --- Схемы для пользователя ---

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

# --- Схемы для элементов списка ---

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ItemRead(ItemBase):
    id: int
    list_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# Новая схема для публичного отображения элемента со статусом бронирования
class ItemPublicRead(ItemBase):
    id: int
    is_reserved: bool = False # По умолчанию не забронировано
    class Config:
        from_attributes = True

# --- Схемы для списков ---

class ListBase(BaseModel):
    title: str
    description: Optional[str] = None
    list_type: ListType = ListType.WISHLIST
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE
    theme_name: ThemeName = ThemeName.DEFAULT

class ListCreate(ListBase):
    pass

class ListUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    list_type: Optional[ListType] = None
    privacy_level: Optional[PrivacyLevel] = None
    theme_name: Optional[ThemeName] = None

class ListRead(ListBase):
    id: int
    owner_id: int
    public_url_key: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ItemRead] = []
    class Config:
        from_attributes = True

# Новая схема для публичного отображения списка с публичными элементами
class ListPublicRead(ListBase):
    id: int
    items: List[ItemPublicRead] = []
    class Config:
        from_attributes = True

# --- Схемы для бронирования ---

# Схема для отображения бронирования в списке пользователя
class ReservationRead(BaseModel):
    id: int
    item_id: int
    item: ItemRead # Включаем полную информацию об элементе
    created_at: datetime

    class Config:
        from_attributes = True