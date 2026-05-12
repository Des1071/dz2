from celery import Celery
from dotenv import load_dotenv
import os

# Загружаем .env файл
load_dotenv()

# Берем переменные из окружения (которые загружены из .env)
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672//')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

print(f"Celery Config from .env:")
print(f"  Broker: {RABBITMQ_URL}")
print(f"  Backend: {REDIS_URL}")

celery_app = Celery(
    "bot_service",
    broker=RABBITMQ_URL,
    backend=REDIS_URL,
    include=["app.tasks.llm_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

if __name__ == "__main__":
    celery_app.start()
