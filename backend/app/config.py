from __future__ import annotations
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./data/investment_analyzer.db"
    JWT_SECRET_KEY: str
    JWT_ACCESS_EXPIRE_MINUTES: int = 480
    JWT_REFRESH_EXPIRE_DAYS: int = 30
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    ANGEL_ONE_API_KEY: Optional[str] = None

    @model_validator(mode="after")
    def check_required_fields(self) -> "Settings":
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY is required and cannot be empty")
        return self


settings = Settings()
