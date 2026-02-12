
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Invoice Builder API"
    
    # Database
    PGHOST: str = "ep-delicate-grass-a13wuz83-pooler.ap-southeast-1.aws.neon.tech"
    PGDATABASE: str = "invoice_builder"
    PGUSER: str = "neondb_owner"
    PGPASSWORD: str = "npg_At4EhSTQM7He"
    PGSSLMODE: str = "require"
    
    @computed_field
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}/{self.PGDATABASE}?ssl={self.PGSSLMODE}"

    # Security
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SECURE_SECRET_KEY" # Should be env var in prod
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

settings = Settings()
