from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

from app.core.config import settings
from app.bot.dispatcher import create_bot_and_dispatcher
from app.infra.redis import close_redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 50)
    logger.info("Starting Bot Service...")
    logger.info(f"Bot token: {settings.telegram_bot_token[:15]}...")
    logger.info(f"Redis URL: {settings.redis_url}")
    logger.info(f"RabbitMQ URL: {settings.rabbitmq_url}")
    logger.info("=" * 50)
    
    # Create bot and dispatcher
    bot, dp = await create_bot_and_dispatcher()
    
    # Start bot polling
    async def start_bot():
        try:
            logger.info("Starting bot polling...")
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Bot polling error: {e}", exc_info=True)
        finally:
            await bot.session.close()
    
    task = asyncio.create_task(start_bot())
    app.state.bot_task = task
    
    logger.info("Bot service started successfully!")
    yield
    
    # Shutdown
    logger.info("Shutting down Bot Service...")
    await close_redis()
    if hasattr(app.state, 'bot_task'):
        app.state.bot_task.cancel()
    logger.info("Bot service stopped")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.app_name}

@app.get("/")
async def root():
    return {"message": "Bot Service is running", "docs": "/docs"}
