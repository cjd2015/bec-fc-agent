from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="BEC Agent API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    db_driver: str = Field(default="postgresql", alias="DB_DRIVER")
    db_host: str = Field(default="127.0.0.1", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="bec_agent", alias="DB_NAME")
    db_user: str = Field(default="bec_user", alias="DB_USER")
    db_password: str = Field(default="change_this", alias="DB_PASSWORD")
    database_url_raw: Optional[str] = Field(default=None, alias="DATABASE_URL")

    jwt_secret: str = Field(default="change_this_secret", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, alias="JWT_EXPIRE_MINUTES")

    cors_allow_origins_raw: str = Field(default="http://localhost:3000", alias="CORS_ALLOW_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")

    model_provider: str = Field(default="qwen", alias="MODEL_PROVIDER")
    model_base_url: str = Field(default="", alias="MODEL_BASE_URL")
    model_api_key: str = Field(default="", alias="MODEL_API_KEY")
    model_name: str = Field(default="", alias="MODEL_NAME")
    model_timeout_seconds: int = Field(default=60, alias="MODEL_TIMEOUT_SECONDS")

    @property
    def cors_allow_origins(self) -> List[str]:
        return [item.strip() for item in self.cors_allow_origins_raw.split(",") if item.strip()]

    @property
    def database_url(self) -> str:
        if self.database_url_raw:
            return self.database_url_raw
        if self.db_driver.startswith("postgres"):
            password = quote_plus(self.db_password)
            return f"postgresql+psycopg2://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return f"sqlite:///./{self.db_name}.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
