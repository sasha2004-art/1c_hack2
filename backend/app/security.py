from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from passlib.context import CryptContext
from jose import JWTError, jwt

# --- Настройки безопасности ---

# 1. Контекст для хеширования паролей
# Используем pbkdf2_sha256 — не требует нативных bcrypt-зависимостей и хорошо подходит для тестов/MVP
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# 2. Настройки JWT
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise EnvironmentError("SECRET_KEY environment variable not set!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --- Утилиты для паролей ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# --- Утилиты для JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
