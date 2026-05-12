import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_get_redis():
    """Тест получения Redis клиента"""
    with patch('app.infra.redis.redis.from_url') as mock_from_url:
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        mock_from_url.return_value = mock_client
        
        from app.infra.redis import get_redis
        client = await get_redis()
        assert client is not None


@pytest.mark.asyncio
async def test_close_redis():
    """Тест закрытия Redis соединения"""
    with patch('app.infra.redis.redis.from_url') as mock_from_url:
        mock_client = AsyncMock()
        mock_from_url.return_value = mock_client
        
        from app.infra.redis import get_redis, close_redis
        await get_redis()
        await close_redis()
        
        mock_client.close.assert_called_once()
