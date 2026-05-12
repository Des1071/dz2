import logging
import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from app.core.jwt import decode_and_validate, InvalidTokenError, TokenExpiredError
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"Start command from user {message.from_user.id}")
    await message.answer(
        "Салам попалам\n\n"
        "Получи токен:\n"
        "1. Регистрация http://localhost:8000/docs\n"
        "2. Залогинься\n"
        "3. Отправь /token твой токен \n\n"
        "Сделай это"
    )


@router.message(Command("token"))
async def cmd_token(message: types.Message):
    logger.info(f"Token command from user {message.from_user.id}")
    
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer("❌ Введи токен: /token <your_jwt_token>")
        return
    
    token = args[1].strip()
    logger.info(f"Token received, length: {len(token)}")
    
    try:
        payload = decode_and_validate(token)
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        
        redis = await get_redis()
        key = f"token:{message.from_user.id}"
        await redis.setex(key, 3600, token)
        
        await message.answer(
            f"✅ Token проверен!\n"
            f"User ID: {user_id}\n"
            f"Role: {role}\n\n"
            f"К делу!"
        )
        logger.info(f"Токен сохранен для юзера {message.from_user.id}")
        
    except TokenExpiredError:
        await message.answer("❌ Получи новый токен")
    except InvalidTokenError as e:
        await message.answer(f"❌ Не тот token: {str(e)}")
    except Exception as e:
        logger.error(f"Error saving token: {e}")
        await message.answer(f"❌ Ошибка токена: {str(e)}")


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📋 Команды:\n"
        "/start - \n"
        "/token <jwt> - Токен\n"
        "/help - Хэлп\n\n"
        
    )


@router.message()
async def handle_message(message: types.Message):
    logger.info(f"Message from user {message.from_user.id}: {message.text[:50]}...")
    
    try:
        redis = await get_redis()
        key = f"token:{message.from_user.id}"
        token = await redis.get(key)
        
        if not token:
            await message.answer(
                "🔒 Токен не найден.\n"
                "Отправь: /token <your_jwt_token>"
            )
            return
        
        # Validate token
        payload = decode_and_validate(token)
        logger.info(f"Valid token for user {message.from_user.id}: {payload.get('sub')}")
        
        # Send to Celery
        await message.answer("🤔 Processing your request...")
        llm_request.delay(message.from_user.id, message.text)
        logger.info(f"Task sent to Celery for user {message.from_user.id}")
        
        # Wait for response
        for i in range(30):
            await asyncio.sleep(1)
            response_key = f"response:{message.from_user.id}"
            response = await redis.get(response_key)
            if response:
                await message.answer(response)
                await redis.delete(response_key)
                return
        
        await message.answer("⏰ Таймаут")
        
    except TokenExpiredError:
        await message.answer("🔒 Просрочен токен")
        await redis.delete(key)
    except InvalidTokenError as e:
        await message.answer(f"❌ не тот токен: {str(e)}")
        await redis.delete(key)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await message.answer(f"❌ Error: {str(e)}")