from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from . import crud, models, schemas, security
from .db.base import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False) # auto_error=False делает токен опциональным

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    # Эта зависимость по-прежнему требует токен
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = security.decode_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user

# --- НОВАЯ ФУНКЦИЯ ---
def get_optional_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[models.User]:
    """
    Возвращает текущего пользователя, если токен предоставлен и валиден.
    В противном случае возвращает None, не вызывая ошибку.
    """
    if token is None:
        return None
    
    payload = security.decode_token(token)
    if payload is None:
        return None

    email: str = payload.get("sub")
    if email is None:
        return None

    user = crud.get_user_by_email(db, email=email)
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
