import httpx
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Клиент для работы с OpenRouter API.
    Использует модель openrouter/free (бесплатный эндпоинт)
    """
    
    def __init__(self):
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        
    async def chat_completion(self, prompt: str) -> Optional[str]:
        """
        Отправляет запрос к OpenRouter API и возвращает ответ.
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        }
        
        payload = {
            "model": self.model,  # openrouter/free
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        
        logger.info(f"📤 Sending request to OpenRouter")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Prompt length: {len(prompt)} chars")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0].get("message", {}).get("content", "")
                        
                        if content:
                            logger.info(f"✅ Response received, length: {len(content)} chars")
                            return content.strip()
                        else:
                            logger.warning("⚠️ Empty response from OpenRouter")
                            return "Извините, я не смог сгенерировать ответ."
                    else:
                        logger.error(f"❌ Unexpected response format")
                        return "Ошибка формата ответа от API."
                        
                elif response.status_code == 401:
                    logger.error("❌ Authentication error")
                    return "Ошибка авторизации. Проверьте API ключ OpenRouter."
                    
                elif response.status_code == 429:
                    logger.error("❌ Rate limit exceeded")
                    return "Превышен лимит запросов. Попробуйте позже."
                    
                else:
                    error_text = response.text
                    logger.error(f"❌ API error {response.status_code}: {error_text}")
                    return f"Ошибка API: {response.status_code}"
                    
            except httpx.TimeoutException:
                logger.error("❌ OpenRouter API timeout")
                return "Превышено время ожидания ответа от API. Попробуйте позже."
                
            except httpx.ConnectError:
                logger.error("❌ Cannot connect to OpenRouter API")
                return "Не удалось подключиться к API. Проверьте интернет-соединение."
                
            except Exception as e:
                logger.error(f"❌ OpenRouter error: {e}", exc_info=True)
                return f"Произошла ошибка: {str(e)}"


openrouter_client = OpenRouterClient()
