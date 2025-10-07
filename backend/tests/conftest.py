import os
import pytest
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError

# Импортируем наше приложение FastAPI и базовый класс для моделей
from app.main import app
from app.db.base import Base, get_db

# --- НАСТРОЙКА ТЕСТОВОЙ БАЗЫ ДАННЫХ ---

# Получаем данные для подключения к основной БД из переменных окружения
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASS = os.environ.get("POSTGRES_PASSWORD")
DB_HOST = os.environ.get("POSTGRES_SERVER")
DB_NAME_MAIN = os.environ.get("POSTGRES_DB")

# Имя тестовой БД
DB_NAME_TEST = f"{DB_NAME_MAIN}_test"

# URL для подключения к СУЩЕСТВУЮЩЕЙ (основной) базе, чтобы оттуда создать тестовую
SQLALCHEMY_MAIN_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME_MAIN}"
# URL для подключения к ТЕСТОВОЙ базе данных
SQLALCHEMY_TEST_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME_TEST}"


# --- ФИКСТУРЫ PYTEST ---

@pytest.fixture(scope="session")
def db_engine() -> Generator:
    """
    Фикстура, которая создает тестовую базу данных, движок для нее,
    а затем удаляет БД после завершения тестов.
    """
    # Подключаемся к основной БД, чтобы выполнить команду создания новой БД
    main_engine = create_engine(SQLALCHEMY_MAIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
    
    with main_engine.connect() as connection:
        # Пробуем удалить старую тестовую БД, если она осталась от предыдущих запусков
        try:
            connection.execute(text(f"DROP DATABASE {DB_NAME_TEST}"))
        except ProgrammingError:
            pass # Если БД не существует, будет ошибка - это нормально
        
        # Создаем новую, чистую тестовую БД
        connection.execute(text(f"CREATE DATABASE {DB_NAME_TEST}"))

    # Теперь, когда тестовая БД создана, создаем движок для нее
    test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
    
    # Создаем все таблицы
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine # Возвращаем созданный движок для использования в других фикстурах
    
    # После завершения всех тестов удаляем все таблицы и саму тестовую БД
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose() # Закрываем все соединения
    
    with main_engine.connect() as connection:
        connection.execute(text(f"DROP DATABASE {DB_NAME_TEST}"))
    main_engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator:
    """
    Фикстура для предоставления тестовой сессии БД каждому тесту.
    Зависит от фикстуры db_engine.
    """
    connection = db_engine.connect()
    # Начинаем транзакцию
    transaction = connection.begin()
    # Создаем сессию
    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = Session()

    yield session  # Здесь выполняется сам тест
    
    # После завершения теста откатываем транзакцию, чтобы очистить данные
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """
    Фикстура для создания тестового клиента API.
    Она переопределяет зависимость `get_db`, чтобы использовать тестовую сессию.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c