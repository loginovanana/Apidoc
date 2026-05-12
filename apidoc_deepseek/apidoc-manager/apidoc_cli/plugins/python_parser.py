"""Python parser plugin for FastAPI and Flask."""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional

from apidoc_cli.plugins.base import BaseParser


class PythonParserPlugin(BaseParser):
    @property
    def name(self) -> str:
        return "python-parser"
    
    @property
    def frameworks(self) -> List[str]:
        return ["fastapi", "flask"]
    
    def parse(self, source: Path, **kwargs) -> Dict[str, Any]:
        framework = self._detect_framework(source)
        if framework == "fastapi":
            return self._parse_fastapi(source, **kwargs)
        elif framework == "flask":
            return self._parse_flask(source, **kwargs)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _detect_framework(self, source: Path) -> Optional[str]:
        if source.is_file():
            content = source.read_text()
        else:
            for pattern in ["app.py", "main.py", "*/app.py", "*/main.py"]:
                files = list(source.glob(pattern))
                if files:
                    content = files[0].read_text()
                    break
            else:
                raise ValueError("No Python app file found")
        
        if "from fastapi import" in content or "import fastapi" in content:
            return "fastapi"
        elif "from flask import" in content or "import flask" in content:
            return "flask"
        return None
    
    def _parse_fastapi(self, source: Path, **kwargs) -> Dict[str, Any]:
        import sys
        sys.path.insert(0, str(source.parent))
        try:
            if source.is_file():
                module_name = source.stem
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, source)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                import importlib
                module = importlib.import_module(source.name)
            
            app = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, "__class__") and attr.__class__.__name__ == "FastAPI":
                    app = attr
                    break
            
            if not app:
                raise ValueError("No FastAPI app instance found")
            
            openapi_spec = app.openapi()
            if kwargs.get("title"):
                openapi_spec["info"]["title"] = kwargs["title"]
            if kwargs.get("version"):
                openapi_spec["info"]["version"] = kwargs["version"]
            return openapi_spec
        except Exception as e:
            raise RuntimeError(f"Failed to parse FastAPI app: {e}")
        finally:
            sys.path.pop(0)
    
    def _parse_flask(self, source: Path, **kwargs) -> Dict[str, Any]:
        spec = {"openapi": "3.0.3", "info": {"title": kwargs.get("title", source.stem), "version": kwargs.get("version", "1.0.0")}, "paths": {}}
        if source.is_file():
            content = source.read_text()
            tree = ast.parse(content)
            
            class RouteVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.routes = []
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Attribute) and node.func.attr == "route":
                        if len(node.args) > 0 and isinstance(node.args[0], ast.Constant):
                            path = node.args[0].value
                            methods = ["GET"]
                            for kw in node.keywords:
                                if kw.arg == "methods" and isinstance(kw.value, ast.List):
                                    methods = [el.value.upper() for el in kw.value.elts if isinstance(el, ast.Constant)]
                            self.routes.append({"path": path, "methods": methods})
                    self.generic_visit(node)
            
            visitor = RouteVisitor()
            visitor.visit(tree)
            for route in visitor.routes:
                if route["path"] not in spec["paths"]:
                    spec["paths"][route["path"]] = {}
                for method in route["methods"]:
                    spec["paths"][route["path"]][method.lower()] = {"summary": f"{method} {route['path']}", "responses": {"200": {"description": "Successful response"}}}
        return spec
