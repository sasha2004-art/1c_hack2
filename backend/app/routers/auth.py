from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import crud, schemas, security
from ..db.base import get_db

router = APIRouter()


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # --- ДОБАВИТЬ ПРОВЕРКУ НА УНИКАЛЬНОСТЬ ИМЕНИ ---
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # Проверяем имя
    db_user_by_name = db.query(crud.models.User).filter(crud.models.User.name == user.name).first()
    if db_user_by_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is already taken",
        )
    return crud.create_user(db=db, user=user)


# --- ИЗМЕНИТЬ ЭТУ ФУНКЦИЮ ---
@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # Используем новую функцию для поиска по email или имени
    user = crud.get_user_by_email_or_name(db, login_identifier=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # Обновляем сообщение об ошибке
            detail="Incorrect email/name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": user.email} # В токен по-прежнему кладем email, это стандарт
    )

    return {"access_token": access_token, "token_type": "bearer"}
