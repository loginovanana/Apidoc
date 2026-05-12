"""Server configuration."""

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APIDOC_", env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    
    host: str = Field("0.0.0.0")
    port: int = Field(8000, ge=1, le=65535)
    debug: bool = Field(False)
    log_level: str = Field("INFO")
    log_json: bool = Field(True)
    secret_key: str = Field("change-me-in-production")
    allowed_hosts: List[str] = Field(["*"])
    cors_origins: List[str] = Field(["*"])
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str): return [origin.strip() for origin in v.split(",")]
        return v
    
    database_url: str = Field("sqlite+aiosqlite:///./apidoc.db")
    database_pool_size: int = Field(20, ge=1)
    database_max_overflow: int = Field(10, ge=0)
    redis_url: Optional[str] = Field(None)
    enable_docs: bool = Field(True)
    rate_limit_per_minute: int = Field(60)
    rate_limit_per_hour: int = Field(1000)
    data_dir: Path = Field(Path("./data"))
    upload_max_size: int = Field(10 * 1024 * 1024)
    enable_metrics: bool = Field(True)
    token_expire_minutes: int = Field(1440)
    
    def model_post_init(self, __context) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
