# ===================================================================
# ЭТАП 1: Сборка статических файлов Vue.js
# ===================================================================
FROM node:18-alpine AS build-frontend

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app/frontend

# Копируем package.json и package-lock.json для кэширования зависимостей
COPY frontend/package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код фронтенда
COPY frontend/ .

# Собираем production-версию приложения
RUN npm run build


# ===================================================================
# ЭТАП 2: Создание финального образа Nginx для фронтенда
# ===================================================================
FROM nginx:stable-alpine AS final-frontend

# Копируем собранные файлы из предыдущего этапа `build-frontend`
COPY --from=build-frontend /app/frontend/dist /usr/share/nginx/html

# Копируем кастомный конфиг Nginx
COPY frontend/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80
EXPOSE 80

# Команда для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]


# ===================================================================
# ЭТАП 3: Подготовка зависимостей для бэкенда Python
# ===================================================================
FROM python:3.11-slim AS build-backend

# Установка системных зависимостей для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и устанавливаем зависимости Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ===================================================================
# ЭТАП 4: Создание финального образа FastAPI для бэкенда
# ===================================================================
FROM python:3.11-slim AS final-backend

WORKDIR /app

# Копируем установленные зависимости из этапа `build-backend`
COPY --from=build-backend /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=build-backend /usr/local/bin/ /usr/local/bin/

# Копируем код нашего FastAPI приложения
COPY backend/ .

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]