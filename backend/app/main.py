from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from .db.base import engine, get_db
from . import models
# Импортируем все роутеры
from .routers import auth, users, lists, items, public, reservations, interactions, friends

# Создаем все таблицы в БД, которые унаследованы от Base
models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="Plotix Blog Backend")

# Список источников, которым разрешено делать запросы к вашему API
origins = [
    "http://localhost",
    "http://localhost:80", 
    "http://localhost:5173" # Добавлен порт для режима разработки Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,      
    allow_methods=["*"],         
    allow_headers=["*"],         
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(lists.router, prefix="/lists", tags=["lists"])
app.include_router(items.router, prefix="", tags=["items"])
app.include_router(public.router, prefix="/public", tags=["public"])
app.include_router(reservations.router)
app.include_router(interactions.router)
# (Задача 5.1) Регистрируем новый роутер для друзей
app.include_router(friends.router)


@app.get("/")
def read_root():
    return {"message": "Plotix Blog Backend is running!"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db_connection": "successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")