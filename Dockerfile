# =================================================================
# ЭТАП 1: Сборка Frontend (Vue.js)
# =================================================================
# Называем этот этап 'frontend-builder', чтобы ссылаться на него позже
FROM node:18-alpine AS frontend-builder

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app/frontend

# Копируем package.json и package-lock.json для установки зависимостей
COPY frontend/package*.json ./
RUN npm install

# Копируем весь остальной код фронтенда
COPY frontend/ ./

# Собираем приложение в статические файлы. Результат будет в /app/frontend/dist
RUN npm run build


# =================================================================
# ЭТАП 2: Сборка Backend (FastAPI) и финального образа
# =================================================================
# Используем тот же образ Python, что и в вашем backend/Dockerfile
FROM python:3.11-slim

# Установка системных зависимостей для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости Python
# Путь теперь ./backend/requirements.txt, так как Dockerfile в корне
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код бэкенда
COPY backend/ ./

# --- КЛЮЧЕВОЙ ШАГ ---
# Копируем собранные статические файлы из этапа 'frontend-builder'
# в папку, которую FastAPI будет раздавать
COPY --from=frontend-builder /app/frontend/dist /app/static/frontend


# Команда для запуска приложения
# Запускаем uvicorn из папки 'app', где находится main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]