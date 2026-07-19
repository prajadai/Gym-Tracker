from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./gym.db"
    secret_key: str = "change-me-in-production"  # used later for JWT
    admin_secret_key: str = "for-admin-only"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()