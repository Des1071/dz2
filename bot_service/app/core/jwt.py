from typing import Dict, Any
from jose import JWTError, jwt

from app.core.config import settings


class InvalidTokenError(Exception):
    pass


class TokenExpiredError(Exception):
    pass


def decode_and_validate(token: str) -> Dict[str, Any]:

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg]
        )
        
        # Check required fields
        if "sub" not in payload:
            raise InvalidTokenError("Missing 'sub' field")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except JWTError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")