import pytest
import sys
from pathlib import Path

# Добавляем путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

# Настройка для тестов


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Мок переменных окружения для тестов"""
    import os
    os.environ.setdefault('JWT_SECRET', 'test_secret_key_for_jwt')
    os.environ.setdefault('JWT_ALG', 'HS256')
    os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')
    os.environ.setdefault('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672//')
    os.environ.setdefault('OPENROUTER_API_KEY', 'test_key')
    os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'test_token_12345')
    os.environ.setdefault('OPENROUTER_MODEL', 'test/model')
    yield
