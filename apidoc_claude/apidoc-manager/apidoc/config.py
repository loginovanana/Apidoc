"""Configuration management for APIDoc CLI."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

HOME_DIR = Path.home() / ".apidoc"
LOG_DIR  = HOME_DIR / "logs"
DATA_DIR = HOME_DIR / "data"
for _d in (HOME_DIR, LOG_DIR, DATA_DIR):
    _d.mkdir(parents=True, exist_ok=True)

class Settings:
    server_url:       str           = os.getenv("APIDOC_SERVER_URL", "http://localhost:8000")
    server_timeout:   int           = int(os.getenv("APIDOC_SERVER_TIMEOUT", "30"))
    db_url:           str           = os.getenv("APIDOC_DB_URL",
                                        f"sqlite+aiosqlite:///{DATA_DIR / 'apidoc.db'}")
    validator_url:    str           = os.getenv("APIDOC_VALIDATOR_URL",
                                        "https://validator.swagger.io")
    log_level:        str           = os.getenv("APIDOC_LOG_LEVEL", "INFO")
    log_file:         Path          = Path(os.getenv("APIDOC_LOG_FILE",
                                        str(LOG_DIR / "apidoc.log")))
    default_format:   str           = os.getenv("APIDOC_OUTPUT_FORMAT", "yaml")
    swaggerhub_token: Optional[str] = os.getenv("APIDOC_SWAGGERHUB_TOKEN")
    swaggerhub_owner: Optional[str] = os.getenv("APIDOC_SWAGGERHUB_OWNER")
    github_token:     Optional[str] = os.getenv("APIDOC_GITHUB_TOKEN")
    github_repo:      Optional[str] = os.getenv("APIDOC_GITHUB_REPO")
    gitlab_token:     Optional[str] = os.getenv("APIDOC_GITLAB_TOKEN")
    gitlab_project_id:Optional[str] = os.getenv("APIDOC_GITLAB_PROJECT_ID")
    redocly_token:    Optional[str] = os.getenv("APIDOC_REDOCLY_TOKEN")
    readme_token:     Optional[str] = os.getenv("APIDOC_README_TOKEN")
    readme_version:   Optional[str] = os.getenv("APIDOC_README_VERSION")
    jwt_secret:       Optional[str] = os.getenv("APIDOC_JWT_SECRET")

    @classmethod
    def mask(cls, value: Optional[str]) -> str:
        if not value:
            return "<not set>"
        return value[:4] + "****" if len(value) > 4 else "****"

settings = Settings()

def setup_logging(debug: bool = False) -> None:
    import sys
    logger.remove()
    level = "DEBUG" if debug else settings.log_level
    logger.add(sys.stderr, level=level, colorize=True,
               format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
    logger.add(settings.log_file, level="DEBUG", rotation="50 MB", retention="30 days",
               compression="zip",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}",
               encoding="utf-8")
