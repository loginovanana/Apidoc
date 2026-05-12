"""Spec loading/saving utilities."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import yaml
from apidoc.utils.errors import ParseError

def load_spec(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists(): raise FileNotFoundError(f"File not found: {path}")
    try:
        text = p.read_text(encoding="utf-8")
        return json.loads(text) if p.suffix.lower() == ".json" else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ParseError(f"Failed to parse {path}: {exc}", str(exc)) from exc

def save_spec(spec: dict[str, Any], path: str | Path, fmt: str = "yaml") -> None:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(spec, indent=2, ensure_ascii=False)
                 if fmt == "json" else yaml.dump(spec, allow_unicode=True, sort_keys=False),
                 encoding="utf-8")

def spec_to_str(spec: dict[str, Any], fmt: str = "yaml") -> str:
    return (json.dumps(spec, indent=2, ensure_ascii=False)
            if fmt == "json" else yaml.dump(spec, allow_unicode=True, sort_keys=False))

def detect_format(path: str | Path) -> str:
    return "json" if Path(path).suffix.lower() == ".json" else "yaml"
