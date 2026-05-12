
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "bot-service"
    env: str = "local"
    
    # Telegram
    telegram_bot_token: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # JWT
    jwt_secret: str = os.getenv('JWT_SECRET', 'change_me_super_secret_12345')
    jwt_alg: str = os.getenv('JWT_ALG', 'HS256')
    
    # Redis & RabbitMQ
    redis_url: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    rabbitmq_url: str = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672//')
    
    # OpenRouter - используем openrouter/free
    openrouter_api_key: str = os.getenv('OPENROUTER_API_KEY', '')
    openrouter_base_url: str = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    openrouter_model: str = os.getenv('OPENROUTER_MODEL', 'openrouter/free')
    openrouter_site_url: str = os.getenv('OPENROUTER_SITE_URL', 'http://localhost:8001')
    openrouter_app_name: str = os.getenv('OPENROUTER_APP_NAME', 'bot-service')
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
print("=" * 50)
print("Settings loaded from .env:")
print(f"  TELEGRAM_BOT_TOKEN: {settings.telegram_bot_token[:15]}...")
print(f"  REDIS_URL: {settings.redis_url}")
print(f"  RABBITMQ_URL: {settings.rabbitmq_url}")
print(f"  OPENROUTER_MODEL: {settings.openrouter_model}")
print("=" * 50)
