
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Настройка bcrypt с ограничением длины
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=True  # Будет выдавать ошибку при превышении
)

def hash_password(password: str) -> str:
    """Хэш пароля"""
    try:
        # Обрезаем пароль до 72 байт (проблема bcrypt)
        password_bytes = password.encode('utf-8')[:72]
        truncated_password = password_bytes.decode('utf-8', errors='ignore')
        
        if len(password) > 72:
            logger.warning(f"Password truncated from {len(password)} to 72 bytes")
        
        logger.info(f"Hashing password (length: {len(truncated_password)} bytes)")
        hashed = pwd_context.hash(truncated_password)
        logger.info("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password """
    try:
        # Обрезаем проверяемый пароль так же
        password_bytes = plain_password.encode('utf-8')[:72]
        truncated_password = password_bytes.decode('utf-8', errors='ignore')
        
        logger.info("Verifying password")
        result = pwd_context.verify(truncated_password, hashed_password)
        logger.info(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def create_access_token(user_id: int, role: str = "user") -> str:
    """Create JWT access token"""
    try:
        logger.info(f"Creating token for user_id: {user_id}")
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "role": role,
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_expire_minutes)
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)
        logger.info("Token created successfully")
        return token
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token"""
    try:
        logger.info("Decoding token")
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_alg]
        )
        logger.info(f"Token decoded successfully, sub: {payload.get('sub')}")
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise ValueError(f"Invalid token: {str(e)}")
