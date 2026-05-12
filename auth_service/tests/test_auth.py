import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Тест health check"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Тест регистрации пользователя"""
    response = await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "123456"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Тест регистрации с существующим email"""
    # Первая регистрация
    await client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "123456"}
    )
    
    # Вторая регистрация с тем же email
    response = await client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "123456"}
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Тест успешного входа"""
    # Регистрация
    await client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "123456"}
    )
    
    # Логин
    response = await client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "123456"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Тест входа с неверными данными"""
    response = await client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_me_without_token(client: AsyncClient):
    """Тест доступа без токена"""
    response = await client.get("/auth/me")
    assert response.status_code == 401
