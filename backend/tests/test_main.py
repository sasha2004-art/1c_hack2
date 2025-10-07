from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

# Тест 1: Проверка основного эндпоинта ("/")
def test_read_root(client: TestClient):
    """
    Проверяем, что корневой эндпоинт '/' возвращает успешный ответ
    и ожидаемое сообщение.
    """
    response = client.get("/")
    assert response.status_code == 200
    json_response = response.json()
    assert "message" in json_response
    assert json_response["message"] == "Plotix Blog Backend is running!"

# Тест 2: Проверка эндпоинта состояния здоровья ("/health")
def test_health_check(client: TestClient):
    """
    Проверяем эндпоинт '/health', который должен подтвердить,
    что подключение к базе данных успешно.
    """
    response = client.get("/health")
    # Проверяем, что запрос прошел успешно (код 200)
    assert response.status_code == 200
    # Проверяем, что тело ответа содержит ожидаемый статус
    assert response.json() == {"status": "ok", "db_connection": "successful"}

# Тест 3: Прямая проверка создания и чтения модели User
def test_user_model_in_db(db_session: Session):
    """
    Этот тест напрямую работает с тестовой базой данных, чтобы убедиться,
    что модель User корректно создается и сохраняется.
    """
    from app.models import User

    # Создаем экземпляр модели User
    test_user = User(
        email="test@example.com",
        hashed_password="somehashedpassword",
        is_active=True
    )

    # Добавляем его в сессию и сохраняем в БД
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # Проверяем, что пользователю был присвоен id
    assert test_user.id is not None
    # Проверяем, что email соответствует заданному
    assert test_user.email == "test@example.com"

    # Дополнительная проверка: пытаемся найти этого пользователя в БД
    user_from_db = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user_from_db is not None
    assert user_from_db.id == test_user.id