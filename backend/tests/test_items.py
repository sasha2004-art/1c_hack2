from fastapi.testclient import TestClient

# Вспомогательная функция для получения заголовков аутентификации
def get_user_auth_headers(client: TestClient, email="itemuser@example.com", password="itempassword") -> dict:
    client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    login_response = client.post(
        "/auth/token",
        data={"username": email, "password": password},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Вспомогательная функция для создания списка
def create_list_for_user(client: TestClient, headers: dict) -> int:
    response = client.post(
        "/lists/",
        headers=headers,
        json={"title": "Test List for Items"},
    )
    assert response.status_code == 201
    return response.json()["id"]

def test_create_item_in_list(client: TestClient):
    headers = get_user_auth_headers(client)
    list_id = create_list_for_user(client, headers)

    response = client.post(
        f"/lists/{list_id}/items",
        headers=headers,
        json={"title": "My first item", "description": "A great item"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My first item"
    assert data["list_id"] == list_id
    assert "id" in data

def test_read_items_in_list(client: TestClient):
    headers = get_user_auth_headers(client)
    list_id = create_list_for_user(client, headers)
    
    # Создаем два элемента
    client.post(f"/lists/{list_id}/items", headers=headers, json={"title": "Item 1"})
    client.post(f"/lists/{list_id}/items", headers=headers, json={"title": "Item 2"})

    # Получаем список со всеми элементами
    response = client.get(f"/lists/{list_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == list_id
    assert len(data["items"]) == 2
    assert data["items"][0]["title"] == "Item 1"
    assert data["items"][1]["title"] == "Item 2"

def test_update_item(client: TestClient):
    headers = get_user_auth_headers(client)
    list_id = create_list_for_user(client, headers)
    create_response = client.post(f"/lists/{list_id}/items", headers=headers, json={"title": "Item to update"})
    item_id = create_response.json()["id"]

    update_response = client.put(
        f"/items/{item_id}",
        headers=headers,
        json={"title": "Updated Item Title", "details": {"url": "http://example.com"}},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated Item Title"
    assert data["details"]["url"] == "http://example.com"
    assert data["id"] == item_id

def test_delete_item(client: TestClient):
    headers = get_user_auth_headers(client)
    list_id = create_list_for_user(client, headers)
    create_response = client.post(f"/lists/{list_id}/items", headers=headers, json={"title": "Item to delete"})
    item_id = create_response.json()["id"]

    delete_response = client.delete(f"/items/{item_id}", headers=headers)
    assert delete_response.status_code == 200
    
    # Проверяем, что элемент удален
    list_response = client.get(f"/lists/{list_id}", headers=headers)
    assert len(list_response.json()["items"]) == 0

def test_update_item_not_owner(client: TestClient):
    # Пользователь 1 создает список и элемент
    headers1 = get_user_auth_headers(client, "user1@example.com", "pass1")
    list_id = create_list_for_user(client, headers1)
    create_res = client.post(f"/lists/{list_id}/items", headers=headers1, json={"title": "Owned by user 1"})
    item_id = create_res.json()["id"]

    # Пользователь 2 пытается обновить этот элемент
    headers2 = get_user_auth_headers(client, "user2@example.com", "pass2")
    update_response = client.put(f"/items/{item_id}", headers=headers2, json={"title": "Attempted update"})
    assert update_response.status_code == 403