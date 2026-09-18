from fastapi.testclient import TestClient


def test_register_login_and_read_profile(client: TestClient) -> None:
    registration = client.post(
        "/api/auth/register",
        json={"name": "Mouid Test", "email": "Mouid@Example.com", "password": "securepass123"},
    )
    assert registration.status_code == 201
    assert registration.json()["user"]["email"] == "mouid@example.com"

    token = registration.json()["access_token"]
    profile = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["name"] == "Mouid Test"

    login = client.post(
        "/api/auth/login",
        json={"email": "mouid@example.com", "password": "securepass123"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_rejects_duplicate_account_and_bad_password(client: TestClient) -> None:
    payload = {"name": "First User", "email": "user@example.com", "password": "securepass123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409

    bad_login = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "wrong-password"},
    )
    assert bad_login.status_code == 401
    assert client.get("/api/auth/me").status_code == 401
