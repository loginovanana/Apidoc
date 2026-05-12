"""Go parser plugin."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from apidoc_cli.plugins.base import BaseParser


class GoParserPlugin(BaseParser):
    @property
    def name(self) -> str:
        return "go-parser"
    
    @property
    def frameworks(self) -> List[str]:
        return ["gin", "echo", "fiber"]
    
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        framework = self._detect_framework(source)
        if framework == "gin":
            return self._parse_gin(source, **kwargs)
        elif framework == "echo":
            return self._parse_echo(source, **kwargs)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _detect_framework(self, source: Path) -> Optional[str]:
        if source.is_dir():
            go_mod = source / "go.mod"
            if go_mod.exists():
                content = go_mod.read_text()
                if "gin-gonic/gin" in content: return "gin"
                elif "labstack/echo" in content: return "echo"
                elif "gofiber/fiber" in content: return "fiber"
            for go_file in source.rglob("*.go"):
                content = go_file.read_text()
                if "gin." in content: return "gin"
                elif "echo." in content: return "echo"
        return None
    
    def _parse_gin(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "Gin API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for go_file in source.rglob("*.go"):
            content = go_file.read_text()
            methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
            for method in methods:
                pattern = rf'\.{method}\s*\(\s*["\']([^"\']+)["\']'
                for match in re.finditer(pattern, content):
                    path = match.group(1)
                    if path not in spec["paths"]:
                        spec["paths"][path] = {}
                    spec["paths"][path][method.lower()] = {"summary": f"{method} {path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
    
    def _parse_echo(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "Echo API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for go_file in source.rglob("*.go"):
            content = go_file.read_text()
            methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
            for method in methods:
                pattern = rf'e\.{method}\s*\(\s*["\']([^"\']+)["\']'
                for match in re.finditer(pattern, content):
                    path = match.group(1)
                    if path not in spec["paths"]:
                        spec["paths"][path] = {}
                    spec["paths"][path][method.lower()] = {"summary": f"{method} {path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
