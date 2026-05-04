"""Задание 11.1: unit-тесты трёх эндпоинтов in-memory реестра через TestClient."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

REG_URL = "/registry/accounts"


class TestRegisterAccount:
    def test_register_returns_201_and_payload(self) -> None:
        r = client.post(REG_URL, json={"username": "alice", "email": "alice@example.com"})
        assert r.status_code == 201
        data = r.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["id"] == 1

    def test_register_duplicate_username_409(self) -> None:
        client.post(REG_URL, json={"username": "bob", "email": "bob1@example.com"})
        r = client.post(REG_URL, json={"username": "bob", "email": "bob2@example.com"})
        assert r.status_code == 409
        assert r.json()["detail"] == "Имя пользователя уже занято"

    def test_register_invalid_email_422(self) -> None:
        r = client.post(REG_URL, json={"username": "c", "email": "not-email"})
        assert r.status_code == 422
        body = r.json()
        assert body["error_code"] == "VALIDATION_ERROR"
        assert "email" in " ".join(body.get("issues", [])).lower()

    def test_register_empty_username_422(self) -> None:
        r = client.post(REG_URL, json={"username": "", "email": "u@example.com"})
        assert r.status_code == 422
        assert r.json()["error_code"] == "VALIDATION_ERROR"

    def test_register_ids_increment(self) -> None:
        a = client.post(REG_URL, json={"username": "u1", "email": "u1@e.com"}).json()["id"]
        b = client.post(REG_URL, json={"username": "u2", "email": "u2@e.com"}).json()["id"]
        assert b == a + 1


class TestGetAccount:
    def test_get_existing_200(self) -> None:
        created = client.post(REG_URL, json={"username": "d", "email": "d@e.com"}).json()
        r = client.get(f"{REG_URL}/{created['id']}")
        assert r.status_code == 200
        assert r.json() == created

    def test_get_missing_404(self) -> None:
        r = client.get(f"{REG_URL}/9999")
        assert r.status_code == 404
        assert r.json()["detail"] == "Учётная запись не найдена"

    def test_get_invalid_id_422(self) -> None:
        r = client.get(f"{REG_URL}/not-int")
        assert r.status_code == 422


class TestDeleteAccount:
    def test_delete_existing_204_empty_body(self) -> None:
        uid = client.post(REG_URL, json={"username": "e", "email": "e@e.com"}).json()["id"]
        r = client.delete(f"{REG_URL}/{uid}")
        assert r.status_code == 204
        assert r.text == ""

    def test_delete_missing_404(self) -> None:
        r = client.delete(f"{REG_URL}/42")
        assert r.status_code == 404
        assert r.json()["detail"] == "Учётная запись не найдена"

    def test_delete_twice_second_404(self) -> None:
        uid = client.post(REG_URL, json={"username": "f", "email": "f@e.com"}).json()["id"]
        assert client.delete(f"{REG_URL}/{uid}").status_code == 204
        r2 = client.delete(f"{REG_URL}/{uid}")
        assert r2.status_code == 404

    def test_get_after_delete_404(self) -> None:
        uid = client.post(REG_URL, json={"username": "g", "email": "g@e.com"}).json()["id"]
        client.delete(f"{REG_URL}/{uid}")
        r = client.get(f"{REG_URL}/{uid}")
        assert r.status_code == 404


class TestRegistryFlow:
    def test_register_get_delete_flow(self) -> None:
        r1 = client.post(REG_URL, json={"username": "flow", "email": "flow@e.com"})
        assert r1.status_code == 201
        uid = r1.json()["id"]
        assert client.get(f"{REG_URL}/{uid}").status_code == 200
        assert client.delete(f"{REG_URL}/{uid}").status_code == 204
        assert client.get(f"{REG_URL}/{uid}").status_code == 404
