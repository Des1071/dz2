
from datetime import datetime
from app.repositories.users import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError

class AuthUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register(self, email: str, password: str) -> dict:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()
        
        hashed = hash_password(password)
        user = await self.user_repo.create(email, hashed)
        return {
            "id": user.id, 
            "email": user.email, 
            "role": user.role,
            "created_at": user.created_at
        }
    
    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token(user.id, user.role)
    
    async def get_me(self, token: str) -> dict:
        try:
            payload = decode_token(token)
            user_id = int(payload.get("sub"))
        except Exception as e:
            raise InvalidCredentialsError()
        
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        return {
            "id": user.id, 
            "email": user.email, 
            "role": user.role, 
            "created_at": user.created_at
        }
