import pytest
from jose import jwt

from app.core.jwt import decode_and_validate, InvalidTokenError, TokenExpiredError
from app.core.config import settings


def test_decode_valid_token():
    """Test decoding valid token"""
    # Create test token
    token = jwt.encode(
        {"sub": "123", "role": "user"},
        settings.jwt_secret,
        algorithm=settings.jwt_alg
    )
    
    payload = decode_and_validate(token)
    assert payload["sub"] == "123"
    assert payload["role"] == "user"


def test_decode_invalid_token():
    """Test decoding invalid token"""
    with pytest.raises(InvalidTokenError):
        decode_and_validate("invalid.token.here")


def test_decode_token_missing_sub():
    """Test token without required sub field"""
    token = jwt.encode(
        {"role": "user"},
        settings.jwt_secret,
        algorithm=settings.jwt_alg
    )
    
    with pytest.raises(InvalidTokenError) as exc_info:
        decode_and_validate(token)
    assert "Missing 'sub' field" in str(exc_info.value)