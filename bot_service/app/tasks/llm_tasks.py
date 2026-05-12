import asyncio
import logging
from celery import shared_task
from app.services.openrouter_client import openrouter_client
from app.infra.redis import get_redis

logger = logging.getLogger(__name__)


@shared_task(name="llm_request")
def llm_request(tg_chat_id: int, prompt: str):
    """Process LLM request"""
    logger.info(f"Processing for {tg_chat_id}: {prompt[:50]}...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        response = loop.run_until_complete(
            openrouter_client.chat_completion(prompt)
        )
        
        if not response:
            response = "Sorry, I couldn't generate a response."
        
        loop.run_until_complete(store_response(tg_chat_id, response))
        logger.info(f"Response stored for {tg_chat_id}")
        
    except Exception as e:
        logger.error(f"Task failed: {e}")
        response = f"Error: {str(e)}"
        loop.run_until_complete(store_response(tg_chat_id, response))
    
    finally:
        loop.close()
    
    return {"chat_id": tg_chat_id, "response": response}


async def store_response(chat_id: int, response: str):
    """Store response in Redis"""
    try:
        redis_client = await get_redis()
        key = f"response:{chat_id}"
        await redis_client.setex(key, 300, response)
        logger.info(f"Stored response for {chat_id}")
    except Exception as e:
        logger.error(f"Failed to store response: {e}")