"""Задание 10.2: проверка кастомной обработки RequestValidationError через TestClient."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "username": "ivan",
    "age": 25,
    "email": "ivan@example.com",
    "password": "secret123",
}


def test_create_user_valid() -> None:
    r = client.post("/users", json=VALID_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "ivan"
    assert data["age"] == 25
    assert data["email"] == "ivan@example.com"
    assert data["phone"] == "Unknown"


def test_validation_age_not_gt_18() -> None:
    bad = {**VALID_PAYLOAD, "age": 18}
    r = client.post("/users", json=bad)
    assert r.status_code == 422
    body = r.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert body["detail"] == "Неверные данные запроса"
    assert any("age" in issue for issue in body["issues"])


def test_validation_invalid_email() -> None:
    bad = {**VALID_PAYLOAD, "email": "not-an-email"}
    r = client.post("/users", json=bad)
    assert r.status_code == 422
    body = r.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert any("email" in issue for issue in body["issues"])


def test_validation_password_too_short() -> None:
    bad = {**VALID_PAYLOAD, "password": "short"}
    r = client.post("/users", json=bad)
    assert r.status_code == 422
    body = r.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert any("password" in issue for issue in body["issues"])


def test_validation_missing_required_field() -> None:
    payload = {"username": "x", "age": 30, "email": "x@y.com"}
    r = client.post("/users", json=payload)
    assert r.status_code == 422
    assert r.json()["error_code"] == "VALIDATION_ERROR"
