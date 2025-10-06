# Plotix Blog

Платформа для управления персональными списками (вишлисты, списки дел, книги, фильмы) с системой аутентификации.

## 🚀 Технологический стек

- **Backend:** FastAPI, PostgreSQL, Docker, Pytest
- **Frontend:** Vue.js (v3, Composition API), Pinia, Vue Router, Docker
- **Общее:** Git, Docker Compose

## 📋 Описание проекта

Plotix Blog - это веб-приложение для создания и управления персональными списками. Пользователи могут создавать различные типы списков (вишлисты, списки дел, списки книг, фильмов), управлять ими через удобный интерфейс и делиться публичными списками.

## 🏗️ Архитектура

Проект состоит из трех основных сервисов:
- **Backend (FastAPI)** - REST API для управления данными
- **Frontend (Vue.js)** - Пользовательский интерфейс
- **Database (PostgreSQL)** - Хранение данных
- **PGAdmin** - Инструмент для управления базой данных

## 📁 Структура проекта

```
.
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── crud.py         # CRUD операции
│   │   ├── db/             # Настройки базы данных
│   │   ├── dependencies.py # Зависимости FastAPI
│   │   ├── main.py         # Точка входа приложения
│   │   ├── models.py       # SQLAlchemy модели
│   │   ├── routers/        # API роутеры
│   │   │   ├── auth.py     # Аутентификация
│   │   │   ├── lists.py    # Управление списками
│   │   │   └── users.py    # Пользователи
│   │   ├── schemas.py      # Pydantic схемы
│   │   └── security.py     # Безопасность (JWT, хеширование)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/              # Тесты
├── frontend/                # Vue.js приложение
│   ├── src/
│   │   ├── components/     # Vue компоненты
│   │   ├── router/         # Vue Router настройки
│   │   ├── store/          # Pinia stores
│   │   ├── views/          # Страницы приложения
│   │   └── main.js         # Точка входа
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml       # Docker Compose конфигурация
├── road_map.md             # План разработки
└── README.md               # Этот файл
```

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Git

### Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/sasha2004-art/1c_hack2.git
   cd 1c_hack2
   ```

2. **Запустите приложение:**
   ```bash
   docker-compose up --build -d
   ```

3. **Проверьте статус:**
   ```bash
   docker-compose ps
   ```

### Доступ к сервисам

- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **PGAdmin:** http://localhost:5050 (email: admin@admin.com, password: admin)

## 🧪 Тестирование

### Backend тесты

```bash
# Запуск всех тестов
docker-compose exec backend pytest

# Запуск тестов для списков
docker-compose exec backend pytest tests/test_lists.py -v
```

## 📊 Прогресс разработки

### ✅ Завершенные этапы

#### Фаза 1: Основа и Аутентификация
- **Этап 1:** Настройка проекта и окружения
- **Этап 2:** Базовая модель пользователя
- **Этап 3:** Реализация регистрации и авторизации (JWT)

#### Фаза 2: Основной функционал
- **Этап 4:** Управление списками (CRUD) ✅ **ЗАВЕРШЕН**

### 🔄 Текущие этапы

- **Этап 5:** Управление элементами списков (CRUD)
- **Этап 6:** Публичный доступ и кастомизация
- **Этап 7:** Реализация бронирования для вишлистов

Подробный план разработки см. в файле [road_map.md](road_map.md).

## 🔧 API Endpoints

### Аутентификация
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/token` - Получение JWT токена

### Пользователи
- `GET /users/me` - Получение данных текущего пользователя

### Списки
- `POST /lists/` - Создание нового списка
- `GET /lists/` - Получение всех списков пользователя
- `GET /lists/{list_id}` - Получение конкретного списка
- `PUT /lists/{list_id}` - Обновление списка
- `DELETE /lists/{list_id}` - Удаление списка

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для вашей фичи (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Создайте Pull Request

## 📝 Лицензия

Этот проект находится под лицензией MIT. См. файл `LICENSE` для подробностей.

## 📞 Контакты

- **Автор:** sasha2004-art
- **Репозиторий:** https://github.com/sasha2004-art/1c_hack2