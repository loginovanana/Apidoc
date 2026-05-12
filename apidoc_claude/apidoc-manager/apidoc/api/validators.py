"""OpenAPI Initiative external validator client."""
from __future__ import annotations
from typing import Any
import httpx
from loguru import logger
from apidoc.config import settings
from apidoc.utils.errors import NetworkError

class ValidationResult:
    def __init__(self, messages: list[dict]):
        self.messages = messages
        self.errors   = [m for m in messages if m.get("level","").upper() == "ERROR"]
        self.warnings = [m for m in messages if m.get("level","").upper() == "WARNING"]
    @property
    def is_valid(self) -> bool: return len(self.errors) == 0
    def to_dict(self) -> dict:
        return {"valid": self.is_valid, "errors": self.errors, "warnings": self.warnings,
                "summary": {"errors": len(self.errors), "warnings": len(self.warnings)}}

def validate_external(spec: dict[str, Any]) -> ValidationResult:
    url = f"{settings.validator_url}/validator/debug"
    logger.debug(f"→ POST {url} (external validation)")
    try:
        r = httpx.post(url, json=spec, timeout=30); r.raise_for_status()
        data = r.json()
        msgs = (data.get("messages") or data.get("schemaValidationMessages") or []
                if isinstance(data, dict) else data or [])
        return ValidationResult(msgs)
    except httpx.ConnectError as e:
        raise NetworkError(f"Cannot reach validator at {settings.validator_url}") from e
    except Exception as e:
        logger.warning(f"External validator error: {e}"); return ValidationResult([])
