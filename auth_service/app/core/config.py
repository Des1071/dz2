from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    app_name: str = "auth-service"
    env: str = "local"
    
    jwt_secret: str = "super_secret_key"
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60
    
    sqlite_path: str = "./auth.db"
    
    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.sqlite_path}"
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()