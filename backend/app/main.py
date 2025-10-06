from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from .db.base import engine, get_db
from . import models
from .routers import auth, users

# Создаем все таблицы в БД, которые унаследованы от Base
models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="Plotix Blog Backend")

# Список источников, которым разрешено делать запросы к вашему API
origins = [
    "http://localhost",
    "http://localhost:80", # Можно явно указать и 80 порт
    # Если вы когда-нибудь будете запускать фронтенд в режиме разработки Vite,
    # может понадобиться добавить и его порт, например: "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Разрешить запросы от указанных источников
    allow_credentials=True,      # Разрешить передачу cookies
    allow_methods=["*"],         # Разрешить все методы (GET, POST, etc.)
    allow_headers=["*"],         # Разрешить все заголовки
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/")
def read_root():
    return {"message": "Plotix Blog Backend is running!"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Попытка выполнить простейший SQL-запрос для проверки соединения с БД
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db_connection": "successful"}
    except Exception as e:
        # Если соединение не удалось, возвращаем ошибку
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")