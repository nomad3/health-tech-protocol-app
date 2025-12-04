from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str
    REDIS_URL: str

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Keys
    ANTHROPIC_API_KEY: str
    STRIPE_SECRET_KEY: str

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
