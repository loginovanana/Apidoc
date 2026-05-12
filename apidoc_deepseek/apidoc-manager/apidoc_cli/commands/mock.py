"""Mock server command."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import typer
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from faker import Faker
from loguru import logger
from rich.console import Console

from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()
fake = Faker()


class MockServer:
    """Mock server based on OpenAPI spec."""
    
    def __init__(self, spec: Dict[str, Any], log_file: Optional[Path] = None):
        self.spec = spec
        self.log_file = log_file
        self.app = FastAPI(title=f"Mock: {spec.get('info', {}).get('title', 'API')}")
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_middleware(self):
        self.app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            if self.log_file:
                log_entry = {"method": request.method, "path": str(request.url.path), "client": request.client.host if request.client else None}
                try:
                    body = await request.body()
                    if body:
                        log_entry["body"] = body.decode()
                except Exception:
                    pass
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
            response = await call_next(request)
            return response
    
    def _resolve_ref(self, ref: str) -> Dict[str, Any]:
        """Resolve a JSON $ref pointer within the spec."""
        if not ref.startswith("#/"):
            return {}
        parts = ref[2:].split("/")
        current = self.spec
        for part in parts:
            current = current.get(part, {})
        return current
    
    def _setup_routes(self):
        for path, methods in self.spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                self._add_route(path, method, details)
    
    def _add_route(self, path: str, method: str, details: Dict[str, Any]):
        async def mock_handler(request: Request, path=path, method=method, details=details):
            responses = details.get("responses", {})
            
            # Determine success status code from spec
            success_codes = [code for code in responses.keys() if code.startswith("2")]
            status_code = int(success_codes[0]) if success_codes else 200
            response_schema = responses.get(success_codes[0]) if success_codes else None
            
            if not response_schema:
                return Response(
                    content=json.dumps({"message": f"Mock response for {method.upper()} {path}"}),
                    status_code=status_code,
                    media_type="application/json"
                )
            
            content = response_schema.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                # Resolve $ref if present
                if "$ref" in schema:
                    schema = self._resolve_ref(schema["$ref"])
                # Resolve $ref in items
                if schema.get("type") == "array" and "$ref" in schema.get("items", {}):
                    schema["items"] = self._resolve_ref(schema["items"]["$ref"])
                mock_data = self._generate_mock_data(schema)
            else:
                mock_data = {"message": f"Mock response for {method.upper()} {path}"}
            
            if method.lower() in ["post", "put"]:
                try:
                    request_data = await request.json()
                    mock_data["received"] = request_data
                except Exception:
                    pass
            
            return Response(
                content=json.dumps(mock_data, default=str),
                status_code=status_code,
                media_type="application/json"
            )
        
        route_path = path.replace("{", "<").replace("}", ">")
        route_methods = {"get": self.app.get, "post": self.app.post, "put": self.app.put, "delete": self.app.delete, "patch": self.app.patch}
        if method.lower() in route_methods:
            route_methods[method.lower()](route_path)(mock_handler)
    
    def _generate_mock_data(self, schema: Dict[str, Any]) -> Any:
        # Resolve $ref recursively
        if "$ref" in schema:
            schema = self._resolve_ref(schema["$ref"])
        
        schema_type = schema.get("type", "object")
        
        if schema_type == "object":
            result = {}
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            for prop_name, prop_schema in properties.items():
                if prop_name in required or fake.boolean(chance_of_getting_true=70):
                    result[prop_name] = self._generate_mock_data(prop_schema)
            return result
        elif schema_type == "array":
            items = schema.get("items", {})
            # Resolve $ref in items
            if "$ref" in items:
                items = self._resolve_ref(items["$ref"])
            count = fake.random_int(min=schema.get("minItems", 1), max=schema.get("maxItems", 5))
            return [self._generate_mock_data(items) for _ in range(count)]
        elif schema_type == "string":
            format_type = schema.get("format", "")
            if format_type == "email": return fake.email()
            elif format_type == "date": return fake.date()
            elif format_type == "date-time": return fake.iso8601()
            elif format_type == "uuid": return fake.uuid4()
            elif format_type == "uri": return fake.url()
            else:
                enum = schema.get("enum")
                if enum: return fake.random_element(enum)
                return fake.word()
        elif schema_type == "integer":
            return fake.random_int(min=schema.get("minimum", 0), max=schema.get("maximum", 100))
        elif schema_type == "number":
            return fake.pyfloat(min_value=schema.get("minimum", 0.0), max_value=schema.get("maximum", 100.0))
        elif schema_type == "boolean":
            return fake.boolean()
        else:
            return None
    
    def run(self, host: str = "127.0.0.1", port: int = 8000):
        uvicorn.run(self.app, host=host, port=port, log_level="info")


@app.callback()
def mock_command(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    log_file: Optional[Path] = typer.Option(None, "--log-file", help="Log requests to file"),
) -> None:
    """Start mock server from OpenAPI specification."""
    
    try:
        spec = read_input(spec_file)
        console.print(f"[bold green]Starting mock server for:[/] {spec.get('info', {}).get('title', 'API')}")
        console.print(f"[cyan]Server running at:[/] http://{host}:{port}")
        console.print("\n[yellow]Available endpoints:[/]")
        for path, methods in spec.get("paths", {}).items():
            for method in methods.keys():
                console.print(f"  {method.upper():<7} {path}")
        console.print("\n[dim]Press Ctrl+C to stop[/]\n")
        
        server = MockServer(spec, log_file)
        server.run(host, port)
    except KeyboardInterrupt:
        console.print("\n[yellow]Mock server stopped[/]")
    except Exception as e:
        logger.error(f"Mock server failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if ctx.obj.get("debug"):
            console.print_exception()
        raise typer.Exit(1)