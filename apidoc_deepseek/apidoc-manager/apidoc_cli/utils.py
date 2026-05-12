"""Utility functions for APIDoc CLI."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from loguru import logger


def detect_framework(source: Path) -> Optional[str]:
    if source.is_file():
        content = source.read_text()
    elif source.is_dir():
        markers = {"fastapi": ["fastapi", "FastAPI"], "flask": ["flask", "Flask"]}
        for py_file in source.rglob("*.py"):
            try:
                content = py_file.read_text()
                for framework, patterns in markers.items():
                    if any(pattern in content for pattern in patterns):
                        return framework
            except Exception:
                continue
        return None
    else:
        return None
    
    frameworks = {"fastapi": ["from fastapi", "import fastapi"], "flask": ["from flask", "import flask"]}
    for framework, patterns in frameworks.items():
        if any(pattern in content for pattern in patterns):
            return framework
    return None


def write_output(data: Dict[str, Any], output_path: Path, format: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if format.lower() == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif format.lower() in ["yaml", "yml"]:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    else:
        raise ValueError(f"Unsupported format: {format}")
    logger.debug(f"Written output to {output_path}")


def read_input(input_path: Path) -> Dict[str, Any]:
    content = input_path.read_text(encoding="utf-8")
    if input_path.suffix == ".json":
        return json.loads(content)
    elif input_path.suffix in [".yaml", ".yml"]:
        return yaml.safe_load(content)
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")


def get_version() -> str:
    try:
        from importlib.metadata import version
        return version("apidoc-manager")
    except Exception:
        return "0.1.0"
