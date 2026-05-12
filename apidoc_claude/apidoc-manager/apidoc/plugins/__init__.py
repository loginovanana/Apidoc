"""Plugin system."""
from __future__ import annotations
from abc import ABC, abstractmethod
from importlib.metadata import entry_points
from typing import Any
from loguru import logger
from apidoc.utils.errors import PluginError

class GeneratorPlugin(ABC):
    @abstractmethod
    def generate(self, source_path: str, options: dict[str, Any]) -> dict[str, Any]: ...

class TestGenPlugin(ABC):
    @abstractmethod
    def generate(self, spec: dict[str, Any], output_dir: str,
                 base_url: str, options: dict[str, Any]) -> list[str]: ...

def load_plugins(group: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for ep in entry_points(group=group):
        try:
            result[ep.name] = ep.load()
        except Exception as exc:
            raise PluginError(f"Failed to load plugin '{ep.name}'", str(exc)) from exc
    return result
