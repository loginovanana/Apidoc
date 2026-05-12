"""Configuration management for APIDoc CLI."""

from pathlib import Path
from typing import Optional

import yaml
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseModel):
    url: str = "http://localhost:8000"
    token: Optional[str] = None
    timeout: int = 30


class ExternalServiceConfig(BaseModel):
    swaggerhub_api_key: Optional[str] = None
    github_token: Optional[str] = None
    gitlab_token: Optional[str] = None
    readme_api_key: Optional[str] = None


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: Path = Path.home() / ".apidoc" / "logs" / "apidoc.log"
    rotation: str = "10 MB"
    retention: str = "7 days"
    json_format: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APIDOC_", env_nested_delimiter="__", extra="ignore")
    
    server: ServerConfig = Field(default_factory=ServerConfig)
    external: ExternalServiceConfig = Field(default_factory=ExternalServiceConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    default_output_format: str = "yaml"
    cache_dir: Path = Path.home() / ".apidoc" / "cache"


class Config:
    DEFAULT_CONFIG_PATH = Path.home() / ".apidoc" / "config.yaml"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.settings = Settings()
        self._load()
    
    def _load(self) -> None:
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = yaml.safe_load(f)
                    if data:
                        for key, value in data.items():
                            if hasattr(self.settings, key):
                                getattr(self.settings, key).update(value)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        self.settings = Settings()
    
    def save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.safe_dump(self.settings.model_dump(), f)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        return cls(config_path)


def setup_logging(debug: bool = False, log_file: Optional[Path] = None) -> None:
    import sys
    
    from loguru import logger
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    logger.add(sys.stderr, format=fmt, level=level, colorize=True)
    
    if log_file or debug:
        log_path = log_file or Path.home() / ".apidoc" / "logs" / "apidoc.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(log_path, format=fmt, level="DEBUG", rotation="10 MB", retention="7 days", colorize=False)
