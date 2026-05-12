import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from app.core.config import settings
from app.bot.handlers import router

logger = logging.getLogger(__name__)

async def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    logger.info("Creating bot...")
    
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Проверка подключения
    me = await bot.get_me()
    logger.info(f"✅ Bot connected: @{me.username} (ID: {me.id})")
    
    dp = Dispatcher()
    dp.include_router(router)
    
    logger.info("✅ Dispatcher created")
    return bot, dp