# --- Этап 1: Сборка Vue-приложения ---
FROM node:18-alpine AS build-stage

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта и устанавливаем зависимости
COPY package*.json ./
RUN npm install

# Копируем остальной код и запускаем сборку
COPY . .
RUN npm run build

# --- Этап 2: Развертывание через Nginx ---
FROM nginx:stable-alpine AS production-stage

# Копируем кастомный конфиг Nginx
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранные статические файлы из этапа сборки
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Порт, который слушает Nginx
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]