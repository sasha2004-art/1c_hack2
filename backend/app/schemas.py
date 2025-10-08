from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .models import ListType, PrivacyLevel, ThemeName, FriendshipStatus, NotificationType, GoalType

# --- Схемы для пользователя ---

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str

# Упрощенная схема для отображения в комментариях
class UserInComment(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        from_attributes = True

class UserRead(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

# --- (Задача 3.1) Новые схемы для системы друзей ---

class FriendshipBase(BaseModel):
    id: int
    status: FriendshipStatus

    class Config:
        from_attributes = True

class IncomingRequestRead(FriendshipBase):
    requester: UserInComment # Кто отправил заявку

class OutgoingRequestRead(FriendshipBase):
    addressee: UserInComment # Кому отправили заявку

class FriendRead(BaseModel):
    friend_details: UserInComment
    friendship_id: int

    class Config:
        from_attributes = True

class FriendsAndRequestsResponse(BaseModel):
    friends: List[FriendRead] = []
    incoming_requests: List[IncomingRequestRead] = []
    outgoing_requests: List[OutgoingRequestRead] = []

# --- (Новое) Схемы для уведомлений ---
class NotificationRead(BaseModel):
    id: int
    is_read: bool
    type: NotificationType
    created_at: datetime
    sender: UserInComment # Информация о том, кто совершил действие
    related_item_id: Optional[int] = None
    related_list_id: Optional[int] = None # <--- ДОБАВЛЕНО ЭТО ПОЛЕ
    
    class Config:
        from_attributes = True

class NotificationsResponse(BaseModel):
    unread_count: int
    notifications: List[NotificationRead]

# (Задача 2.1) Новые схемы для страницы профиля
class PublicListForProfile(BaseModel):
    """Упрощенная схема списка для отображения в профиле."""
    id: int
    public_url_key: UUID # <--- ДОБАВЛЕНО ПОЛЕ
    title: str
    list_type: ListType
    privacy_level: PrivacyLevel

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    """Схема для ответа на запрос профиля пользователя."""
    user_info: UserInComment
    public_lists: List[PublicListForProfile]
    friendship_status: Optional[str] # e.g., "friends", "request_sent", "request_received", "none"
    friendship_id: Optional[int] = None # ID для отмены/удаления

# --- Схемы для комментариев ---

class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int
    owner_id: int
    item_id: int
    created_at: datetime
    owner: UserInComment # Включаем информацию о владельце
    
    class Config:
        from_attributes = True

# --- (Этап 13) Новые схемы для Целей ---

class GoalTrackerBase(BaseModel):
    goal_type: GoalType
    target_value: Optional[float] = None
    target_count: Optional[int] = None
    unit_name: Optional[str] = None

class GoalTrackerCreate(GoalTrackerBase):
    pass

class GoalTrackerRead(GoalTrackerBase):
    id: int
    item_id: int
    current_value: float

    class Config:
        from_attributes = True

# (НОВАЯ СХЕМА)
class GoalTrackerUpdate(BaseModel):
    goal_type: Optional[GoalType] = None
    target_value: Optional[float] = None
    target_count: Optional[int] = None
    unit_name: Optional[str] = None

class GoalLogCreate(BaseModel):
    value: float

# --- Схемы для элементов списка ---

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class ItemCreate(ItemBase):
    # (Этап 13) Опциональное поле для создания цели вместе с элементом
    goal_settings: Optional[GoalTrackerCreate] = None

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    # (Этап 13) Поле для ручной отметки о завершении (для обычных элементов)
    is_completed: Optional[bool] = None

# (Этап 10) Схема для запроса копирования элемента
class ItemCopy(BaseModel):
    target_list_id: int

class ItemRead(ItemBase):
    id: int
    list_id: int
    is_completed: bool # (Этап 13) Добавлено поле
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Новые поля для лайков и комментов
    likes_count: int = 0
    is_liked_by_current_user: bool = False
    comments: List[CommentRead] = []

    # (Этап 13) Добавлено поле для данных трекера
    goal_tracker: Optional[GoalTrackerRead] = None

    class Config:
        from_attributes = True

# Новая схема для публичного отображения элемента со статусом бронирования
class ItemPublicRead(ItemBase):
    id: int
    is_reserved: bool = False # По умолчанию не забронировано
    
    # Новые поля для лайков и комментов
    likes_count: int = 0
    comments: List[CommentRead] = []

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
    owner: UserInComment  # <--- ДОБАВЛЕНО ЭТО ПОЛЕ
    items: List[ItemPublicRead] = []
    class Config:
        from_attributes = True

# --- (Этап 11) Новая схема для ленты ---
class ListForFeedRead(ListBase):
    id: int
    public_url_key: UUID # <--- ДОБАВЛЕНО ПОЛЕ
    owner: UserInComment # Включаем информацию о владельце
    created_at: datetime
    items_count: int = 0 # Включаем количество элементов для контекста

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

# --- Схемы для настроек пользователя ---

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class EmailUpdate(BaseModel):
    current_password: str
    new_email: EmailStr