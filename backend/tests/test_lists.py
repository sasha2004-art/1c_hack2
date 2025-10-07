import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def get_user_auth_headers(client: TestClient) -> dict:
    # Регистрация
    client.post(
        "/auth/register",
        json={"email": "listuser@example.com", "password": "listpassword"},
    )
    # Логин
    login_response = client.post(
        "/auth/token",
        data={"username": "listuser@example.com", "password": "listpassword"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_list(client: TestClient):
    headers = get_user_auth_headers(client)
    response = client.post(
        "/lists/",
        headers=headers,
        json={"title": "My First Wishlist", "description": "Things I want"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Wishlist"
    assert "id" in data
    assert "owner_id" in data


def test_create_list_no_auth(client: TestClient):
    response = client.post(
        "/lists/",
        json={"title": "My First Wishlist"},
    )
    assert response.status_code == 401 # Not authenticated


def test_read_user_lists(client: TestClient):
    headers = get_user_auth_headers(client)
    # Создаем еще один список для проверки
    client.post("/lists/", headers=headers, json={"title": "My First List"})
    client.post("/lists/", headers=headers, json={"title": "My Second List"})
    
    response = client.get("/lists/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2 # Как минимум два списка, созданных в этом тесте
    assert data[0]["title"] == "My First List"
    assert data[1]["title"] == "My Second List"


def test_update_list(client: TestClient):
    headers = get_user_auth_headers(client)
    # Сначала создаем список, чтобы его обновить
    create_response = client.post(
        "/lists/",
        headers=headers,
        json={"title": "To be updated"},
    )
    list_id = create_response.json()["id"]

    # Обновляем
    update_response = client.put(
        f"/lists/{list_id}",
        headers=headers,
        json={"title": "Updated Title", "privacy_level": "public"},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Title"
    assert data["privacy_level"] == "public"
    assert data["id"] == list_id


def test_delete_list(client: TestClient):
    headers = get_user_auth_headers(client)
    # Создаем список для удаления
    create_response = client.post(
        "/lists/",
        headers=headers,
        json={"title": "To be deleted"},
    )
    list_id = create_response.json()["id"]

    # Удаляем
    delete_response = client.delete(f"/lists/{list_id}", headers=headers)
    assert delete_response.status_code == 200
    
    # Проверяем, что он удален (должен вернуть 404)
    get_response = client.get(f"/lists/{list_id}", headers=headers)
    assert get_response.status_code == 404


def test_update_list_not_owner(client: TestClient):
    # Создаем список под первым пользователем
    headers1 = get_user_auth_headers(client)
    create_response = client.post(
        "/lists/", headers=headers1, json={"title": "Owned by user 1"}
    )
    list_id = create_response.json()["id"]

    # Создаем второго пользователя и пытаемся обновить из-под него
    client.post("/auth/register", json={"email": "other@example.com", "password": "otherpassword"})
    login_res = client.post("/auth/token", data={"username": "other@example.com", "password": "otherpassword"})
    other_token = login_res.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    update_response = client.put(
        f"/lists/{list_id}", headers=other_headers, json={"title": "Attempted update"}
    )
    assert update_response.status_code == 403 # Forbidden

def test_create_list_with_theme(client: TestClient):
    """Тест: создание списка с указанием темы."""
    headers = get_user_auth_headers(client)
    response = client.post(
        "/lists/",
        headers=headers,
        json={
            "title": "My Themed List",
            "theme_name": "lavender"  # Используем ID темы
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Themed List"
    assert data["theme_name"] == "lavender"

def test_update_list_theme(client: TestClient):
    """Тест: обновление темы существующего списка."""
    headers = get_user_auth_headers(client)
    # Создаем список с темой по умолчанию
    create_response = client.post(
        "/lists/",
        headers=headers,
        json={"title": "List to re-theme"},
    )
    list_id = create_response.json()["id"]
    assert create_response.json()["theme_name"] == "default"

    # Обновляем тему
    update_response = client.put(
        f"/lists/{list_id}",
        headers=headers,
        json={"theme_name": "coffee"},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["theme_name"] == "coffee"

def test_read_public_list_success(client: TestClient):
    """Тест: успешное получение публичного списка по ключу."""
    headers = get_user_auth_headers(client)
    # Создаем список и делаем его публичным
    create_response = client.post(
        "/lists/",
        headers=headers,
        json={"title": "Public List", "privacy_level": "public"},
    )
    public_key = create_response.json()["public_url_key"]

    # Запрашиваем его без аутентификации
    response = client.get(f"/public/lists/{public_key}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Public List"
    # Убеждаемся, что в ответе нет приватной информации
    assert "owner_id" not in data

def test_read_public_list_forbidden(client: TestClient):
    """Тест: попытка получения приватного списка по публичной ссылке (ошибка 403)."""
    headers = get_user_auth_headers(client)
    # Создаем приватный список (по умолчанию)
    create_response = client.post(
        "/lists/",
        headers=headers,
        json={"title": "Private List"},
    )
    public_key = create_response.json()["public_url_key"]

    # Пытаемся получить доступ
    response = client.get(f"/public/lists/{public_key}")
    assert response.status_code == 403
    assert response.json() == {"detail": "This list is not public"}

def test_read_public_list_not_found(client: TestClient):
    """Тест: попытка получения списка по несуществующему ключу (ошибка 404)."""
    non_existent_key = uuid.uuid4()
    response = client.get(f"/public/lists/{non_existent_key}")
    assert response.status_code == 404