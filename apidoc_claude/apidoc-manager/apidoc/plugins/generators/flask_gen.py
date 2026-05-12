"""Flask source → OpenAPI spec generator."""
from __future__ import annotations
import ast, re
from pathlib import Path
from typing import Any
from apidoc.plugins import GeneratorPlugin

class FlaskGeneratorPlugin(GeneratorPlugin):
    HTTP = {"GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"}

    def generate(self, source_path: str, options: dict[str, Any]) -> dict[str, Any]:
        path = Path(source_path)
        routes: list[dict] = []
        if path.is_file():   routes = self._routes(path)
        elif path.is_dir():
            for f in path.rglob("*.py"): routes.extend(self._routes(f))
        spec: dict[str, Any] = {"openapi": "3.1.0",
                                 "info": {"title": options.get("title", "API"),
                                          "version": options.get("version","1.0.0")},
                                 "paths": {}}
        for r in routes:
            pk = r["path"].replace("<","{{").replace(">","}}") # angle→curly
            # simple type:name pattern: <int:id> → {id}
            pk = re.sub(r"\{\{\w+:(\w+)\}\}", r"{\1}", pk)
            pk = re.sub(r"\{\{(\w+)\}\}", r"{\1}", pk)
            for meth in r["methods"]:
                m = meth.lower()
                op_id = re.sub(r"[^a-zA-Z0-9_]", "_", f"{m}_{pk}").strip("_")
                params = [{"name": p, "in": "path", "required": True,
                           "schema": {"type": "string"}}
                          for p in re.findall(r"{(\w+)}", pk)]
                op: dict = {"operationId": op_id, "summary": r.get("summary",""),
                            "responses": {"200": {"description": "Success"}}}
                if params: op["parameters"] = params
                spec["paths"].setdefault(pk, {})[m] = op
        return spec

    def _routes(self, py_file: Path) -> list[dict]:
        routes = []
        try: tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except Exception: return routes
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
            for dec in node.decorator_list:
                r = self._parse_route(dec)
                if r:
                    r["summary"] = (ast.get_docstring(node) or "").split("\n")[0]
                    routes.append(r)
        return routes

    def _parse_route(self, dec) -> dict | None:
        if not isinstance(dec, ast.Call): return None
        f = dec.func
        if not isinstance(f, ast.Attribute) or f.attr != "route": return None
        args = dec.args
        if not args or not isinstance(args[0], ast.Constant): return None
        methods = ["GET"]
        for kw in dec.keywords:
            if kw.arg == "methods" and isinstance(kw.value, ast.List):
                methods = [e.value for e in kw.value.elts
                           if isinstance(e, ast.Constant) and e.value in self.HTTP]
        return {"path": args[0].value, "methods": methods}
