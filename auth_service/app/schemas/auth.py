from pydantic import BaseModel, EmailStr, Field, validator

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, max_length=72, description="User password (6-72 characters)")
    
    @validator('password')
    def validate_password_length(cls, v):
        # Проверяем байтовую длину
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password too long. Maximum 72 bytes (about 72 ASCII characters or fewer Unicode characters)')
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"