"""Java parser plugin."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from apidoc_cli.plugins.base import BaseParser


class JavaParserPlugin(BaseParser):
    @property
    def name(self) -> str:
        return "java-parser"
    
    @property
    def frameworks(self) -> List[str]:
        return ["spring", "jax-rs"]
    
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        framework = self._detect_framework(source)
        if framework == "spring":
            return self._parse_spring(source, **kwargs)
        elif framework == "jax-rs":
            return self._parse_jaxrs(source, **kwargs)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _detect_framework(self, source: Path) -> Optional[str]:
        if source.is_dir():
            pom = source / "pom.xml"
            if pom.exists():
                content = pom.read_text()
                if "spring-boot" in content: return "spring"
                elif "jax-rs" in content or "javax.ws.rs" in content: return "jax-rs"
            for java_file in source.rglob("*.java"):
                content = java_file.read_text()
                if "@RestController" in content or "@Controller" in content: return "spring"
                elif "@Path" in content: return "jax-rs"
        return None
    
    def _parse_spring(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "Spring API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for java_file in source.rglob("*.java"):
            content = java_file.read_text()
            class_path = ""
            class_match = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']', content)
            if class_match: class_path = class_match.group(1)
            mappings = [("@GetMapping", "get"), ("@PostMapping", "post"), ("@PutMapping", "put"), ("@DeleteMapping", "delete"), ("@PatchMapping", "patch"), ("@RequestMapping", "get")]
            for annotation, method in mappings:
                pattern = rf'{annotation}\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']'
                for match in re.finditer(pattern, content):
                    sub_path = match.group(1)
                    full_path = class_path + sub_path
                    if full_path not in spec["paths"]:
                        spec["paths"][full_path] = {}
                    spec["paths"][full_path][method] = {"summary": f"{method.upper()} {full_path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
    
    def _parse_jaxrs(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", "JAX-RS API"), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        for java_file in source.rglob("*.java"):
            content = java_file.read_text()
            class_path = ""
            class_match = re.search(r'@Path\s*\(\s*["\']([^"\']+)["\']', content)
            if class_match: class_path = class_match.group(1)
            method_annotations = {"@GET": "get", "@POST": "post", "@PUT": "put", "@DELETE": "delete", "@PATCH": "patch"}
            for annotation, method in method_annotations.items():
                if annotation in content:
                    path_match = re.search(rf'{annotation}\s*\n.*?@Path\s*\(\s*["\']([^"\']+)["\']', content, re.DOTALL)
                    sub_path = path_match.group(1) if path_match else ""
                    full_path = class_path + sub_path
                    if full_path not in spec["paths"]:
                        spec["paths"][full_path] = {}
                    spec["paths"][full_path][method] = {"summary": f"{method.upper()} {full_path}", "responses": {"200": {"description": "Successful response"}}}
        return spec
