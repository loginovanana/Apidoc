"""JavaScript/TypeScript parser plugin."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from apidoc_cli.plugins.base import BaseParser


class JSParserPlugin(BaseParser):
    @property
    def name(self) -> str:
        return "js-parser"
    
    @property
    def frameworks(self) -> List[str]:
        return ["express", "nestjs", "fastify"]
    
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        framework = self._detect_framework(source)
        if framework == "express":
            return self._parse_express(source, **kwargs)
        elif framework == "nestjs":
            return self._parse_nestjs(source, **kwargs)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _detect_framework(self, source: Path) -> Optional[str]:
        if source.is_file():
            content = source.read_text()
        else:
            pkg_json = source / "package.json"
            if pkg_json.exists():
                pkg = json.loads(pkg_json.read_text())
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "@nestjs/core" in deps: return "nestjs"
                elif "express" in deps: return "express"
                elif "fastify" in deps: return "fastify"
            for js_file in source.rglob("*.js"):
                content = js_file.read_text()
                if "express()" in content: return "express"
            return None
        
        if "express()" in content: return "express"
        elif "@Module" in content or "@Controller" in content: return "nestjs"
        return None
    
    def _parse_express(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "Express API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        content = source.read_text() if source.is_file() else ""
        route_patterns = [r'app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', r'router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']']
        for pattern in route_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                method = match.group(1).lower()
                path = match.group(2)
                if path not in spec["paths"]:
                    spec["paths"][path] = {}
                spec["paths"][path][method] = {"summary": f"{method.upper()} {path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
    
    def _parse_nestjs(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "NestJS API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for controller_file in source.rglob("*.controller.ts"):
            content = controller_file.read_text()
            prefix_match = re.search(r'@Controller\s*\(\s*["\']([^"\']+)["\']', content)
            prefix = prefix_match.group(1) if prefix_match else ""
            decorators = ["Get", "Post", "Put", "Delete", "Patch"]
            for decorator in decorators:
                pattern = rf'@{decorator}\s*\(\s*["\']([^"\']*)["\']'
                for match in re.finditer(pattern, content):
                    sub_path = match.group(1)
                    full_path = prefix + sub_path
                    if full_path not in spec["paths"]:
                        spec["paths"][full_path] = {}
                    spec["paths"][full_path][decorator.lower()] = {"summary": f"{decorator.upper()} {full_path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
