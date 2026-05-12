"""Production logging configuration."""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from loguru import logger


class JSONFormatter:
    def __call__(self, record: Dict[str, Any]) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "message": record["message"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }
        if record["exception"]:
            log_entry["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
            }
        return json.dumps(log_entry, default=str)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_production_logging(log_level: str = "INFO", log_file: str = "logs/apidoc.json", json_format: bool = True, add_stdout: bool = True) -> None:
    logger.remove()
    handlers = []
    
    if json_format:
        handlers.append({"sink": log_file, "format": JSONFormatter(), "level": log_level, "rotation": "100 MB", "retention": "30 days", "compression": "gz"})
        if add_stdout:
            handlers.append({"sink": sys.stdout, "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", "level": log_level, "colorize": True})
    else:
        handlers.append({"sink": sys.stdout, "format": "{time} | {level} | {message}", "level": log_level})
        handlers.append({"sink": log_file, "format": "{time} | {level} | {message}", "level": "DEBUG", "rotation": "100 MB", "retention": "30 days"})
    
    for handler in handlers:
        logger.add(**handler)
    
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for logger_name in ["uvicorn", "fastapi", "sqlalchemy"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
