from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://strategy_lab:strategy_lab@localhost:5432/strategy_lab",
        validation_alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql://strategy_lab:strategy_lab@localhost:5432/strategy_lab",
        validation_alias="DATABASE_URL_SYNC",
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL",
    )

    # MinIO
    minio_endpoint: str = Field(default="localhost:9000", validation_alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", validation_alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="market-data", validation_alias="MINIO_BUCKET")
    minio_secure: bool = Field(default=False, validation_alias="MINIO_SECURE")

    # API
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    api_workers: int = Field(default=4, validation_alias="API_WORKERS")

    # Frontend
    vite_api_url: str = Field(default="http://localhost:8000", validation_alias="VITE_API_URL")
    vite_ws_url: str = Field(default="ws://localhost:8000", validation_alias="VITE_WS_URL")

    # MCP
    mcp_server_name: str = Field(default="strategy-lab", validation_alias="MCP_SERVER_NAME")
    mcp_server_version: str = Field(default="0.1.0", validation_alias="MCP_SERVER_VERSION")

    # Security
    secret_key: str = Field(default="change-in-production", validation_alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Development
    debug: bool = Field(default=True, validation_alias="DEBUG")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    return Settings()