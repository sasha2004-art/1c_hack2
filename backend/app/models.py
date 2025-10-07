import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID # Импортируем тип UUID
import enum
from .db.base import Base

class User(Base):
    """
    Модель пользователя в базе данных.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    lists = relationship("List", back_populates="owner", cascade="all, delete-orphan")
    # Связь с бронированиями пользователя
    reservations = relationship("Reservation", back_populates="reserver", cascade="all, delete-orphan")


class ListType(str, enum.Enum):
    WISHLIST = "wishlist"
    TODO = "todo"
    BOOKS = "books"
    MOVIES = "movies"

class PrivacyLevel(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"

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
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
    list = relationship("List", back_populates="items")

    # Связь один-к-одному с бронированием
    reservation = relationship("Reservation", back_populates="item", uselist=False, cascade="all, delete-orphan")


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