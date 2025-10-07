from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID # Импортируем UUID
from .models import ListType, PrivacyLevel, ThemeName # Импортируем новый Enum

# --- Схемы для пользователя --- (без изменений)

class UserBase(BaseModel):
    email: EmailStr
    # Добавляем новые поля
    nickname: Optional[str] = Field(None, max_length=25) # Ограничение до 25 символов
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    # Схема для обновления пользователя - все поля необязательны
    email: Optional[EmailStr] = None
    password: Optional[str] = None # Можно обновлять пароль

class UserRead(UserBase):
    id: int
    is_active: bool
    # Новые поля уже в UserBase, так что здесь они будут унаследованы

    class Config:
        from_attributes = True

# --- Схемы для элементов списка --- (ИЗМЕНЕНЫ)

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    # Поле details удалено

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    # Поле details удалено

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
    # Заменяем старые поля на новое
    theme_name: ThemeName = ThemeName.DEFAULT

class ListCreate(ListBase):
    pass

class ListUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    list_type: Optional[ListType] = None
    privacy_level: Optional[PrivacyLevel] = None
    # Добавляем новое поле для обновления
    theme_name: Optional[ThemeName] = None

class ListRead(ListBase):
    id: int
    owner_id: int
    public_url_key: UUID # Добавляем публичный ключ
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: list[ItemRead] = []
    class Config:
        from_attributes = True

# Новая схема для публичного отображения
class ListPublicRead(ListBase):
    id: int
    items: list[ItemRead] = []
    class Config:
        from_attributes = True