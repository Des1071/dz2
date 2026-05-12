
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserPublic(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
