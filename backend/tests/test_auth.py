from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud

def test_register_user_success(client: TestClient, db_session: Session):
    response = client.post(
        "/auth/register",
        json={"email": "testuser@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    assert "is_active" in data
    user_in_db = crud.get_user_by_email(db_session, "testuser@example.com")
    assert user_in_db is not None
    assert user_in_db.email == "testuser@example.com"


def test_register_user_duplicate_email(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "password1"},
    )
    response = client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "password2"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


def test_login_success(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "loginuser@example.com", "password": "correctpassword"},
    )
    response = client.post(
        "/auth/token",
        data={"username": "loginuser@example.com", "password": "correctpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "loginuser2@example.com", "password": "correctpassword"},
    )
    response = client.post(
        "/auth/token",
        data={"username": "loginuser2@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


def test_read_me_success(client: TestClient):
    client.post(
        "/auth/register",
        json={"email": "me_user@example.com", "password": "password"},
    )
    login_response = client.post(
        "/auth/token",
        data={"username": "me_user@example.com", "password": "password"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/users/me", headers=headers)
    assert me_response.status_code == 200
    data = me_response.json()
    assert data["email"] == "me_user@example.com"


def test_read_me_no_token(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
