from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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


class ListType(str, enum.Enum):
    WISHLIST = "wishlist"
    TODO = "todo"
    BOOKS = "books"
    MOVIES = "movies"

class PrivacyLevel(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"

class List(Base):
    """
    Модель списка (например, вишлист, список дел).
    """
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    list_type = Column(Enum(ListType), default=ListType.WISHLIST, nullable=False)
    privacy_level = Column(Enum(PrivacyLevel), default=PrivacyLevel.PRIVATE, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="lists")
    
    # Добавляем связь с элементами
    items = relationship("Item", back_populates="list", cascade="all, delete-orphan")


class Item(Base):
    """
    Модель элемента внутри списка.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    # Поле JSONB для хранения динамических данных (например, URL для вишлиста, автор для книги)
    details = Column(Text, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
    list = relationship("List", back_populates="items")