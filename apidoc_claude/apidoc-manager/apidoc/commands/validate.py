"""Validate command helpers."""
from __future__ import annotations
from typing import Any
from openapi_spec_validator import OpenAPIV30SpecValidator, OpenAPIV31SpecValidator
from openapi_spec_validator.validation.exceptions import OpenAPISpecValidatorError

def _fix_missing_responses(spec: dict) -> dict:
    for pi in spec.get("paths", {}).values():
        for meth, op in pi.items():
            if meth in ("get","post","put","patch","delete") and isinstance(op,dict):
                if not op.get("responses"):
                    op["responses"] = {"200":{"description":"Successful Response"},
                                       "400":{"description":"Bad Request"}}
    return spec

FIX_SUGGESTIONS: list[dict[str, Any]] = [
    {"check": lambda s: not s.get("info",{}).get("version"),
     "message": "Missing info.version",
     "fix": lambda s: s["info"].__setitem__("version","1.0.0") or s,
     "hint": 'Add info.version: "1.0.0"'},
    {"check": lambda s: not s.get("info",{}).get("title"),
     "message": "Missing info.title",
     "fix": lambda s: s["info"].__setitem__("title","My API") or s,
     "hint": 'Add info.title: "My API"'},
    {"check": lambda s: any(not op.get("responses")
                            for pi in s.get("paths",{}).values()
                            for op in pi.values() if isinstance(op,dict)),
     "message": "Operations missing 'responses' block",
     "fix": _fix_missing_responses,
     "hint": "Add default responses (200, 400)"},
]

def _run_local_validation(spec: dict) -> list[str]:
    errors: list[str] = []
    ver = str(spec.get("openapi","")).strip()
    try:
        v = OpenAPIV31SpecValidator(spec) if ver.startswith("3.1") else OpenAPIV30SpecValidator(spec)
        for e in v.iter_errors(): errors.append(str(e.message))
    except OpenAPISpecValidatorError as e: errors.append(str(e))
    except Exception as e: errors.append(f"Validation engine error: {e}")
    return errors
