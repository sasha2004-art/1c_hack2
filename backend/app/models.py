from sqlalchemy import Column, Integer, String, Boolean
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