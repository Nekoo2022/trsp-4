"""Задание 11.2: асинхронные тесты (httpx.AsyncClient + ASGITransport, Faker)."""

import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient

from app.task_11_2_app import app as asgi_app_11_2


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    transport = ASGITransport(app=asgi_app_11_2)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def faker_instance() -> Faker:
    return Faker()


@pytest.mark.asyncio
class TestCreateUserAsync:
    async def test_create_201_structure(
        self, async_client: AsyncClient, faker_instance: Faker
    ) -> None:
        username = faker_instance.user_name()
        age = faker_instance.random_int(min=19, max=90)
        r = await async_client.post("/users", json={"username": username, "age": age})
        assert r.status_code == 201
        data = r.json()
        assert data["id"] == 1
        assert data["username"] == username
        assert data["age"] == age

    async def test_create_boundary_ages(
        self, async_client: AsyncClient, faker_instance: Faker
    ) -> None:
        low = faker_instance.random_int(min=0, max=17)
        r1 = await async_client.post(
            "/users", json={"username": faker_instance.user_name(), "age": low}
        )
        assert r1.status_code == 201
        high = faker_instance.random_int(min=100, max=120)
        r2 = await async_client.post(
            "/users", json={"username": faker_instance.user_name(), "age": high}
        )
        assert r2.status_code == 201
        assert r2.json()["id"] == 2


@pytest.mark.asyncio
class TestGetUserAsync:
    async def test_get_existing_200(
        self, async_client: AsyncClient, faker_instance: Faker
    ) -> None:
        payload = {
            "username": faker_instance.user_name(),
            "age": faker_instance.random_int(min=18, max=65),
        }
        created = (await async_client.post("/users", json=payload)).json()
        uid = created["id"]
        r = await async_client.get(f"/users/{uid}")
        assert r.status_code == 200
        assert r.json() == created

    async def test_get_missing_404(self, async_client: AsyncClient) -> None:
        r = await async_client.get("/users/99999")
        assert r.status_code == 404
        assert r.json()["detail"] == "User not found"


@pytest.mark.asyncio
class TestDeleteUserAsync:
    async def test_delete_existing_204(
        self, async_client: AsyncClient, faker_instance: Faker
    ) -> None:
        uid = (
            await async_client.post(
                "/users",
                json={
                    "username": faker_instance.user_name(),
                    "age": faker_instance.random_int(min=1, max=99),
                },
            )
        ).json()["id"]
        r = await async_client.delete(f"/users/{uid}")
        assert r.status_code == 204
        assert r.text == ""

    async def test_delete_missing_404(self, async_client: AsyncClient) -> None:
        r = await async_client.delete("/users/424242")
        assert r.status_code == 404
        assert r.json()["detail"] == "User not found"

    async def test_delete_twice_second_404(
        self, async_client: AsyncClient, faker_instance: Faker
    ) -> None:
        uid = (
            await async_client.post(
                "/users",
                json={
                    "username": faker_instance.user_name(),
                    "age": faker_instance.random_int(min=1, max=50),
                },
            )
        ).json()["id"]
        assert (await async_client.delete(f"/users/{uid}")).status_code == 204
        r2 = await async_client.delete(f"/users/{uid}")
        assert r2.status_code == 404


@pytest.mark.asyncio
async def test_get_after_delete_404(
    async_client: AsyncClient, faker_instance: Faker
) -> None:
    uid = (
        await async_client.post(
            "/users",
            json={
                "username": faker_instance.user_name(),
                "age": faker_instance.random_int(min=1, max=40),
            },
        )
    ).json()["id"]
    await async_client.delete(f"/users/{uid}")
    r = await async_client.get(f"/users/{uid}")
    assert r.status_code == 404
