"""FastAPI source → OpenAPI spec generator."""
from __future__ import annotations
import ast, re
from pathlib import Path
from typing import Any
from apidoc.plugins import GeneratorPlugin

class FastAPIGeneratorPlugin(GeneratorPlugin):
    def generate(self, source_path: str, options: dict[str, Any]) -> dict[str, Any]:
        path = Path(source_path)
        routes = []
        if path.is_file():   routes = self._routes(path)
        elif path.is_dir():
            for f in path.rglob("*.py"): routes.extend(self._routes(f))
        title = options.get("title", path.stem.title() + " API")
        spec: dict[str, Any] = {"openapi": "3.1.0",
                                 "info": {"title": title, "version": options.get("version","1.0.0")},
                                 "paths": {}}
        for r in routes:
            pk = r["path"]; m = r["method"].lower()
            op_id = re.sub(r"[^a-zA-Z0-9_]", "_", f"{m}_{pk}").strip("_")
            params = [{"name": p, "in": "path", "required": True,
                       "schema": {"type": "string"}}
                      for p in re.findall(r"{(\w+)}", pk)]
            op: dict = {"operationId": op_id, "summary": r.get("summary",""),
                        "responses": {"200": {"description": "Successful Response"}}}
            if params: op["parameters"] = params
            spec["paths"].setdefault(pk, {})[m] = op
        return spec

    def _routes(self, py_file: Path) -> list[dict]:
        routes = []
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except Exception: return routes
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef): continue
            for dec in node.decorator_list:
                m, p = self._parse(dec)
                if m and p:
                    routes.append({"method": m, "path": p,
                                   "summary": (ast.get_docstring(node) or "").split("\n")[0]})
        return routes

    def _parse(self, dec: ast.expr) -> tuple[str,str]:
        if not isinstance(dec, ast.Call): return "","";
        f = dec.func
        if not isinstance(f, ast.Attribute): return "","";
        meth = f.attr.upper()
        if meth not in ("GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"): return "","";
        if dec.args and isinstance(dec.args[0], ast.Constant): return meth, dec.args[0].value
        return "",""
