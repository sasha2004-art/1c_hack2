import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID # Импортируем тип UUID
import enum
from .db.base import Base

# (Новое) Перечисление для типов уведомлений
class NotificationType(str, enum.Enum):
    FRIEND_REQUEST = "friend_request"
    LIKE = "like"
    COMMENT = "comment"

class User(Base):
    """
    Модель пользователя в базе данных.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    lists = relationship("List", back_populates="owner", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="reserver", cascade="all, delete-orphan")
    
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="owner", cascade="all, delete-orphan")
    
    # (Задача 2.2) Новые связи для системы дружбы
    sent_friend_requests = relationship(
        "Friendship", 
        foreign_keys="[Friendship.requester_id]", 
        back_populates="requester", 
        cascade="all, delete-orphan"
    )
    received_friend_requests = relationship(
        "Friendship", 
        foreign_keys="[Friendship.addressee_id]", 
        back_populates="addressee", 
        cascade="all, delete-orphan"
    )
    
    # (Новое) Связь для полученных уведомлений
    notifications = relationship("Notification", foreign_keys="[Notification.recipient_id]", back_populates="recipient", cascade="all, delete-orphan")


class ListType(str, enum.Enum):
    WISHLIST = "wishlist"
    TODO = "todo"
    BOOKS = "books"
    MOVIES = "movies"

class PrivacyLevel(str, enum.Enum):
    PRIVATE = "private"
    # (Задача 2.3) Новое значение для приватности
    FRIENDS_ONLY = "friends_only"
    PUBLIC = "public"

# (Задача 2.1) Новое перечисление для статуса дружбы
class FriendshipStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"

# (Задача 1.1) Создаем Enum для названий тем
class ThemeName(str, enum.Enum):
    DEFAULT = "default"
    LAVENDER = "lavender"
    MINT = "mint"
    SUNNY = "sunny"
    COFFEE = "coffee"
    NAVY = "navy"

class List(Base):
    """
    Модель списка (например, вишлист, список дел).
    """
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    # Новое поле для публичной ссылки, генерируется автоматически
    public_url_key = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)
    
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    list_type = Column(Enum(ListType), default=ListType.WISHLIST, nullable=False)
    privacy_level = Column(Enum(PrivacyLevel), default=PrivacyLevel.PRIVATE, nullable=False)
    
    # (Задача 1.4) Заменяем старые поля на одно поле для темы
    theme_name = Column(Enum(ThemeName), default=ThemeName.DEFAULT, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="lists")
    
    items = relationship("Item", back_populates="list", cascade="all, delete-orphan")


class Item(Base):
    """
    Модель элемента внутри списка.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    # ИЗМЕНЕНИЕ: Поле description теперь имеет тип Text для хранения HTML
    description = Column(Text, nullable=True) 
    
    # Новые поля для изображений
    image_url = Column(String, nullable=True)  # Путь к полному изображению
    thumbnail_url = Column(String, nullable=True)  # Путь к миниатюре
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
    list = relationship("List", back_populates="items")

    # Связь один-к-одному с бронированием
    reservation = relationship("Reservation", back_populates="item", uselist=False, cascade="all, delete-orphan")

    # Новые связи для лайков и комментариев
    likes = relationship("Like", back_populates="item", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="item", cascade="all, delete-orphan", order_by="Comment.created_at")


# Новая модель для бронирования
class Reservation(Base):
    """
    Модель бронирования элемента вишлиста.
    """
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    
    item_id = Column(Integer, ForeignKey("items.id"), unique=True, nullable=False) # Элемент может быть забронирован только один раз
    reserver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    item = relationship("Item", back_populates="reservation")
    reserver = relationship("User", back_populates="reservations")

# --- Новые модели ---

class Like(Base):
    """
    Модель лайка для элемента списка.
    """
    __tablename__ = "likes"

    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    
    item = relationship("Item", back_populates="likes")
    user = relationship("User", back_populates="likes")

class Comment(Base):
    """
    Модель комментария для элемента списка.
    """
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    item = relationship("Item", back_populates="comments")
    owner = relationship("User", back_populates="comments")

# (Задача 2.4) Новая модель Friendship
class Friendship(Base):
    """
    Модель, представляющая дружбу или заявку в друзья.
    """
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    addressee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(FriendshipStatus), default=FriendshipStatus.PENDING, nullable=False)

    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_friend_requests")
    addressee = relationship("User", foreign_keys=[addressee_id], back_populates="received_friend_requests")

    __table_args__ = (
        UniqueConstraint('requester_id', 'addressee_id', name='unique_friendship_request'),
    )

# (Новая) Модель для уведомлений
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    is_read = Column(Boolean, default=False, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Кому предназначено уведомление
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient = relationship("User", foreign_keys=[recipient_id])
    
    # Кто отправил (инициировал действие)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender = relationship("User", foreign_keys=[sender_id])

    # С каким элементом связано уведомление (необязательно)
    related_item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    related_item = relationship("Item")