from pydantic import BaseModel, EmailStr

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