from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    db_url: str
    db_echo: bool = False

    jwt_algorithm: str = "RS256"
    jwt_private_key: str
    jwt_public_key: str
    jwt_access_token_expire_minutes: int = 60
    jwt_response_token_expire_days: int = 7

    api_v1_prefix: str = '/api/v1'
    alembic_prefix: str = '/alembic'

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
