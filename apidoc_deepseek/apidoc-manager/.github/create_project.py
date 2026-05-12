# ═══════════════════════════════════════════════════════════════════
# 4. CLI КОМАНДЫ
# ═══════════════════════════════════════════════════════════════════
print("📁 CLI команды...")

write_file("apidoc_cli/commands/__init__.py", r'''"""CLI commands module."""

from apidoc_cli.commands import convert, diff, generate, mock, publish, server, testgen, tree, validate

__all__ = ["generate", "validate", "diff", "mock", "testgen", "publish", "convert", "server", "tree"]
''')

write_file("apidoc_cli/commands/generate.py", r'''"""Generate OpenAPI specifications from source code."""

from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from apidoc_cli.config import Config
from apidoc_cli.plugins import PluginManager
from apidoc_cli.utils import detect_framework, write_output

app = typer.Typer()
console = Console()


@app.command(name="generate")
def generate(
    ctx: typer.Context,
    source: Path = typer.Argument(..., help="Source file or directory"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("yaml", "--format", "-f", help="Output format (yaml/json)"),
    framework: Optional[str] = typer.Option(None, "--framework", help="Framework to parse"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
    title: Optional[str] = typer.Option(None, "--title", help="API title"),
    version: Optional[str] = typer.Option("1.0.0", "--version", "-v", help="API version"),
) -> None:
    """Generate OpenAPI specification from source code."""
    
    cfg: Config = ctx.obj["config"]
    debug = ctx.obj["debug"]
    
    if interactive:
        spec = _interactive_generation(title, version)
    else:
        if not source.exists():
            console.print(f"[red]Error:[/] Source path '{source}' does not exist")
            raise typer.Exit(1)
        
        detected_framework = framework or detect_framework(source)
        if not detected_framework:
            console.print("[red]Error:[/] Could not detect framework. Please specify with --framework")
            raise typer.Exit(1)
        
        console.print(f"[cyan]Detected framework:[/] {detected_framework}")
        
        plugin_manager = PluginManager()
        plugin = plugin_manager.get_parser(detected_framework)
        
        if not plugin:
            console.print(f"[red]Error:[/] No parser plugin found for {detected_framework}")
            console.print("Available parsers:")
            for name in plugin_manager.list_parsers():
                console.print(f"  * {name}")
            raise typer.Exit(1)
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Parsing source code...", total=None)
            try:
                spec = plugin.parse(source, title=title, version=version)
                progress.update(task, description="[green]✓[/] Parsing complete")
            except Exception as e:
                progress.update(task, description="[red]✗[/] Parsing failed")
                logger.error(f"Failed to parse source: {e}")
                if debug:
                    console.print_exception()
                raise typer.Exit(1)
    
    output_path = output or Path(f"openapi.{format}")
    write_output(spec, output_path, format)
    
    if not ctx.obj.get("json_output"):
        _show_preview(spec)
    
    console.print(f"\n[green]✓[/] Specification saved to [bold]{output_path}[/]")


def _interactive_generation(title: Optional[str], version: str) -> dict:
    console.print(Panel.fit("[bold cyan]Interactive OpenAPI Specification Generator[/]", border_style="cyan"))
    
    if not title:
        title = Prompt.ask("Enter API title", default="My API")
    
    description = Prompt.ask("Enter API description", default="")
    
    spec = {
        "openapi": "3.0.3",
        "info": {"title": title, "version": version, "description": description},
        "servers": [{"url": Prompt.ask("Server URL", default="http://localhost:8000")}],
        "paths": {},
        "components": {"schemas": {}},
    }
    
    console.print("\n[bold]Let's add some endpoints:[/]")
    
    while Confirm.ask("Add an endpoint?", default=True):
        path = Prompt.ask("  Path", default="/users")
        method = Prompt.ask("  HTTP method", choices=["get", "post", "put", "delete", "patch"], default="get").upper()
        
        if path not in spec["paths"]:
            spec["paths"][path] = {}
        
        endpoint = {
            "summary": Prompt.ask("  Summary", default=f"{method} {path}"),
            "operationId": f"{method.lower()}_{path.strip('/').replace('/', '_')}",
            "responses": {"200": {"description": "Successful response", "content": {"application/json": {"schema": {"type": "object"}}}}}
        }
        
        spec["paths"][path][method.lower()] = endpoint
        console.print(f"  [green]✓[/] Added {method} {path}")
    
    return spec


def _show_preview(spec: dict) -> None:
    console.print("\n[bold]Specification Preview:[/]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Method", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Summary")
    
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            table.add_row(method.upper(), path, details.get("summary", ""))
    
    if table.rows:
        console.print(table)
    else:
        console.print("[yellow]No endpoints defined yet[/]")
''')

write_file("apidoc_cli/commands/validate.py", r'''"""Validate OpenAPI specifications."""

from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from apidoc_cli.validators import OpenAPIValidator

app = typer.Typer()
console = Console()


@app.command(name="validate")
def validate(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Strict validation mode"),
    remote: bool = typer.Option(False, "--remote", help="Use remote validator API"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix common issues"),
) -> None:
    """Validate OpenAPI specification."""
    
    debug = ctx.obj["debug"]
    json_output = ctx.obj["json_output"]
    
    if not spec_file.exists():
        console.print(f"[red]Error:[/] File '{spec_file}' does not exist")
        raise typer.Exit(1)
    
    validator = OpenAPIValidator(use_remote=remote)
    
    try:
        results = validator.validate(spec_file, strict=strict)
        
        if json_output:
            import json
            console.print(json.dumps(results, indent=2))
            return
        
        if results["valid"]:
            console.print(Panel("[bold green]✓ Specification is valid![/]", border_style="green"))
            if results.get("warnings"):
                console.print("\n[yellow]Warnings:[/]")
                for warning in results["warnings"]:
                    console.print(f"  * {warning}")
        else:
            console.print(Panel("[bold red]✗ Specification has errors[/]", border_style="red"))
            table = Table(show_header=True, header_style="bold red")
            table.add_column("Type", style="red")
            table.add_column("Location")
            table.add_column("Message")
            for error in results.get("errors", []):
                table.add_row(error.get("type", "error"), error.get("location", ""), error.get("message", ""))
            console.print(table)
            
            if fix and results.get("fixable", []):
                console.print("\n[cyan]Found fixable issues:[/]")
                for issue in results["fixable"]:
                    if typer.confirm(f"Fix {issue['description']}?"):
                        fixed = validator.apply_fix(spec_file, issue)
                        if fixed:
                            console.print(f"  [green]✓[/] Fixed: {issue['description']}")
                        else:
                            console.print(f"  [red]✗[/] Failed to fix: {issue['description']}")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if debug:
            console.print_exception()
        raise typer.Exit(1)
''')

write_file("apidoc_cli/commands/diff.py", r'''"""Compare OpenAPI specifications."""

import json
from pathlib import Path
from typing import Dict, List, Optional

import typer
from deepdiff import DeepDiff
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


@app.command(name="diff")
def diff_command(
    ctx: typer.Context,
    spec1: Path = typer.Argument(..., help="First specification file or server ID"),
    spec2: Optional[Path] = typer.Argument(None, help="Second specification file"),
    from_server: Optional[int] = typer.Option(None, "--from-server", help="Compare server versions"),
    v1: Optional[str] = typer.Option(None, "--v1", help="First version"),
    v2: Optional[str] = typer.Option(None, "--v2", help="Second version"),
    tree_view: bool = typer.Option(False, "--tree", "-t", help="Show as tree"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Compare two OpenAPI specifications."""
    
    debug = ctx.obj.get("debug", False)
    json_format = ctx.obj.get("json_output", False) or json_output
    
    try:
        if from_server:
            spec1_data, spec2_data = _get_server_versions(from_server, v1, v2)
        else:
            if not spec2:
                console.print("[red]Error:[/] Two files required for local comparison")
                raise typer.Exit(1)
            spec1_data = read_input(spec1)
            spec2_data = read_input(spec2)
        
        diff_result = _compare_specs(spec1_data, spec2_data)
        
        if json_format:
            console.print(json.dumps(diff_result, indent=2, default=str))
            return
        
        _display_diff(diff_result, tree_view=tree_view)
        
        breaking_changes = _detect_breaking_changes(diff_result)
        if breaking_changes:
            console.print("\n[bold red]⚠ BREAKING CHANGES DETECTED![/]")
            for change in breaking_changes:
                console.print(f"  * {change}")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Diff failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


def _compare_specs(spec1: Dict, spec2: Dict) -> Dict:
    diff = DeepDiff(spec1, spec2, ignore_order=True, report_repetition=True, verbose_level=2)
    return {
        "added": [str(item) for item in diff.get("dictionary_item_added", [])],
        "removed": [str(item) for item in diff.get("dictionary_item_removed", [])],
        "changed": {str(k): str(v) for k, v in diff.get("values_changed", {}).items()},
        "type_changes": {str(k): str(v) for k, v in diff.get("type_changes", {}).items()},
        "breaking_changes": [],
    }


def _detect_breaking_changes(diff_result: Dict) -> List[str]:
    breaking = []
    for item in diff_result.get("removed", []):
        if "paths" in item:
            breaking.append(f"Removed endpoint: {item}")
    for path, change in diff_result.get("changed", {}).items():
        if "required" in path:
            breaking.append(f"Required field changed: {path}")
    for path, change in diff_result.get("type_changes", {}).items():
        breaking.append(f"Type changed: {path}")
    return breaking


def _display_diff(diff_result: Dict, tree_view: bool = False) -> None:
    if tree_view:
        _display_tree_diff(diff_result)
    else:
        _display_table_diff(diff_result)


def _display_table_diff(diff_result: Dict) -> None:
    if diff_result.get("added"):
        table = Table(title="Added", style="green")
        table.add_column("Path", style="green")
        for item in diff_result["added"][:20]:
            table.add_row(item[:80])
        console.print(table)
    if diff_result.get("removed"):
        table = Table(title="Removed", style="red")
        table.add_column("Path", style="red")
        for item in diff_result["removed"][:20]:
            table.add_row(item[:80])
        console.print(table)
    if diff_result.get("changed"):
        table = Table(title="Changed", style="yellow")
        table.add_column("Path")
        table.add_column("Old Value")
        table.add_column("New Value")
        for path, change in list(diff_result["changed"].items())[:20]:
            table.add_row(path[:40], str(change)[:30], "")
        console.print(table)


def _display_tree_diff(diff_result: Dict) -> None:
    tree = Tree("API Changes")
    if diff_result.get("added"):
        added_branch = tree.add("✅ Added")
        for item in diff_result["added"][:10]:
            added_branch.add(item[:60])
    if diff_result.get("removed"):
        removed_branch = tree.add("❌ Removed")
        for item in diff_result["removed"][:10]:
            removed_branch.add(item[:60])
    if diff_result.get("changed"):
        changed_branch = tree.add("🔄 Changed")
        for path in list(diff_result["changed"].keys())[:10]:
            changed_branch.add(path[:60])
    console.print(tree)


def _get_server_versions(spec_id: int, v1: Optional[str], v2: Optional[str]) -> tuple:
    import httpx
    try:
        response = httpx.get(f"http://localhost:8000/api/v1/specs/{spec_id}", params={"version": v1})
        spec1 = response.json()["content"]
        response = httpx.get(f"http://localhost:8000/api/v1/specs/{spec_id}", params={"version": v2})
        spec2 = response.json()["content"]
        return spec1, spec2
    except Exception as e:
        raise RuntimeError(f"Failed to get server versions: {e}")
''')

write_file("apidoc_cli/commands/mock.py", r'''"""Mock server command."""

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
    
    def _setup_routes(self):
        for path, methods in self.spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                self._add_route(path, method, details)
    
    def _add_route(self, path: str, method: str, details: Dict[str, Any]):
        async def mock_handler(request: Request, path=path, method=method, details=details):
            responses = details.get("responses", {})
            response_schema = None
            for status_code in ["200", "201"]:
                if status_code in responses:
                    response_schema = responses[status_code]
                    break
            
            if not response_schema:
                return Response(content=json.dumps({"message": "Mock response"}), media_type="application/json")
            
            content = response_schema.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                mock_data = self._generate_mock_data(schema)
            else:
                mock_data = {"message": f"Mock response for {method.upper()} {path}"}
            
            if method.lower() in ["post", "put"]:
                try:
                    request_data = await request.json()
                    mock_data["received"] = request_data
                except Exception:
                    pass
            
            return Response(content=json.dumps(mock_data, default=str), media_type="application/json")
        
        route_path = path.replace("{", "<").replace("}", ">")
        route_methods = {"get": self.app.get, "post": self.app.post, "put": self.app.put, "delete": self.app.delete, "patch": self.app.patch}
        if method.lower() in route_methods:
            route_methods[method.lower()](route_path)(mock_handler)
    
    def _generate_mock_data(self, schema: Dict[str, Any]) -> Any:
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


@app.command(name="mock")
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
''')

write_file("apidoc_cli/commands/testgen.py", r'''"""Test generation command."""

from pathlib import Path
from typing import Dict, List

import typer
from loguru import logger
from rich.console import Console
from rich.progress import Progress

from apidoc_cli.plugins import PluginManager
from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


class PytestGenerator:
    """Generate pytest tests from OpenAPI spec."""
    
    def generate(self, spec: Dict, output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        conftest_path = self._generate_conftest(output_dir, spec)
        generated_files.append(conftest_path)
        
        tests_by_tag = self._group_by_tag(spec)
        for tag, endpoints in tests_by_tag.items():
            test_file = self._generate_test_file(output_dir, tag, endpoints, spec)
            generated_files.append(test_file)
        
        return generated_files
    
    def _generate_conftest(self, output_dir: Path, spec: Dict) -> Path:
        base_url = spec.get("servers", [{}])[0].get("url", "http://localhost:8000")
        content = f'''"""Pytest configuration for {spec.get("info", {}).get("title", "API")}."""

import pytest
import httpx


@pytest.fixture
def base_url():
    return "{base_url}"


@pytest.fixture
async def client():
    async with httpx.AsyncClient() as client:
        yield client
'''
        conftest_path = output_dir / "conftest.py"
        conftest_path.write_text(content)
        return conftest_path
    
    def _group_by_tag(self, spec: Dict) -> Dict[str, List]:
        groups = {"default": []}
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                tags = details.get("tags", ["default"])
                for tag in tags:
                    if tag not in groups:
                        groups[tag] = []
                    groups[tag].append({"path": path, "method": method, "details": details})
        return groups
    
    def _generate_test_file(self, output_dir: Path, tag: str, endpoints: List, spec: Dict) -> Path:
        tag_safe = tag.lower().replace(" ", "_").replace("-", "_")
        content = f'''"""Tests for {tag} endpoints."""

import pytest
from httpx import AsyncClient


class Test{tag_safe.title()}API:
    """Test cases for {tag} endpoints."""
    
'''
        for endpoint in endpoints:
            content += self._generate_test_method(endpoint)
        
        test_path = output_dir / f"test_{tag_safe}.py"
        test_path.write_text(content)
        return test_path
    
    def _generate_test_method(self, endpoint: Dict) -> str:
        path = endpoint["path"]
        method = endpoint["method"]
        details = endpoint["details"]
        op_id = details.get("operationId", f"{method}_{path.replace('/', '_')}")
        success_code = "200"
        for code in ["200", "201", "204"]:
            if code in details.get("responses", {}):
                success_code = code
                break
        
        return f'''
    @pytest.mark.asyncio
    async def test_{op_id}(self, client: AsyncClient, base_url: str):
        """Test {method.upper()} {path}"""
        response = await client.{method.lower()}(f"{{base_url}}{path}")
        assert response.status_code == {success_code}
'''


@app.command(name="testgen")
def testgen_command(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    output_dir: Path = typer.Option(Path("./tests"), "--output", "-o", help="Output directory"),
    framework: str = typer.Option("pytest", "--framework", "-f", help="Test framework"),
    language: str = typer.Option("python", "--language", "-l", help="Language"),
) -> None:
    """Generate tests from OpenAPI specification."""
    
    try:
        spec = read_input(spec_file)
        console.print(f"[bold]Generating tests for:[/] {spec.get('info', {}).get('title', 'API')}")
        
        if language == "python" and framework == "pytest":
            generator = PytestGenerator()
        else:
            plugin_manager = PluginManager()
            generator = plugin_manager.get_test_generator(f"{language}-{framework}")
            if not generator:
                console.print(f"[red]Error:[/] No generator found for {language}/{framework}")
                console.print("Available generators:")
                for name in plugin_manager.list_test_generators():
                    console.print(f"  * {name}")
                raise typer.Exit(1)
        
        with Progress() as progress:
            task = progress.add_task("Generating tests...", total=None)
            files = generator.generate(spec, output_dir)
            progress.update(task, description="[green]✓ Tests generated[/]")
        
        console.print(f"\n[green]✓[/] Generated {len(files)} test files in [bold]{output_dir}[/]")
        console.print("\n[cyan]Run tests with:[/]")
        console.print(f"  pytest {output_dir} -v")
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if ctx.obj.get("debug"):
            console.print_exception()
        raise typer.Exit(1)
''')

write_file("apidoc_cli/commands/publish.py", r'''"""Publish command."""

import asyncio
import base64
from pathlib import Path
from typing import Dict, List, Optional

import httpx
import typer
import yaml
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from apidoc_cli.config import Config
from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


class Publisher:
    """Publish specifications to various services."""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def publish_to_server(self, spec: Dict, name: str, server_url: str, token: Optional[str] = None) -> Dict:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{server_url}/api/v1/specs",
                json={"name": name, "content": spec, "format": "json", "changelog": "Published via CLI"},
                headers=headers
            )
            if response.status_code == 409:
                spec_id = await self._get_spec_id(client, server_url, name, headers)
                if spec_id:
                    response = await client.post(
                        f"{server_url}/api/v1/specs/{spec_id}/versions",
                        json={"content": spec, "version": spec.get("info", {}).get("version", "1.0.0"), "format": "json", "changelog": "Updated via CLI"},
                        headers=headers
                    )
            response.raise_for_status()
            return response.json()
    
    async def _get_spec_id(self, client, server_url: str, name: str, headers: Dict) -> Optional[int]:
        response = await client.get(f"{server_url}/api/v1/specs/search", params={"q": name}, headers=headers)
        data = response.json()
        for item in data.get("items", []):
            if item["name"] == name:
                return item["id"]
        return None
    
    async def publish_to_swaggerhub(self, spec: Dict, api_key: str, owner: str, name: str, version: str) -> Dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://api.swaggerhub.com/apis/{owner}/{name}",
                params={"version": version, "isPrivate": "false"},
                json=spec,
                headers={"Authorization": api_key, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    
    async def publish_to_github(self, spec: Dict, token: str, repo: str, path: str, branch: str = "main", message: str = "Update OpenAPI specification") -> Dict:
        yaml_content = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
        content_base64 = base64.b64encode(yaml_content.encode()).decode()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                params={"ref": branch},
                headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            )
            data = {"message": message, "content": content_base64, "branch": branch}
            if response.status_code == 200:
                data["sha"] = response.json()["sha"]
            
            response = await client.put(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                json=data,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            )
            response.raise_for_status()
            result = response.json()
            return {"url": result["content"]["html_url"], "sha": result["content"]["sha"], "path": path}
    
    async def publish_to_readme(self, spec: Dict, api_key: str, version: str) -> Dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://dash.readme.com/api/v1/api-registry",
                json={"spec": spec, "version": version},
                headers={"Authorization": f"Bearer {api_key}"}
            )
            response.raise_for_status()
            return response.json()


@app.command(name="publish")
def publish_command(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    targets: List[str] = typer.Option(["server"], "--target", "-t", help="Publish targets (server, swaggerhub, github, readme)"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="API name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="API version"),
    server_url: Optional[str] = typer.Option(None, "--server-url", help="Server URL"),
    swaggerhub_owner: Optional[str] = typer.Option(None, "--swaggerhub-owner", help="SwaggerHub owner"),
    github_repo: Optional[str] = typer.Option(None, "--github-repo", help="GitHub repository"),
    github_path: Optional[str] = typer.Option(None, "--github-path", help="Path in GitHub repo"),
) -> None:
    """Publish OpenAPI specification to various services."""
    
    cfg: Config = ctx.obj["config"]
    
    try:
        spec = read_input(spec_file)
        api_name = name or spec.get("info", {}).get("title", spec_file.stem)
        api_version = version or spec.get("info", {}).get("version", "1.0.0")
        
        console.print(f"[bold]Publishing:[/] {api_name} v{api_version}")
        
        publisher = Publisher(cfg)
        results = []
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            async def publish_all():
                tasks = []
                
                if "server" in targets:
                    async def pub_server():
                        url = server_url or cfg.server.url
                        return await publisher.publish_to_server(spec, api_name, url, cfg.server.token)
                    tasks.append(("Server", pub_server()))
                
                if "swaggerhub" in targets and cfg.external.swaggerhub_api_key:
                    async def pub_swagger():
                        return await publisher.publish_to_swaggerhub(spec, cfg.external.swaggerhub_api_key, swaggerhub_owner, api_name, api_version)
                    tasks.append(("SwaggerHub", pub_swagger()))
                
                if "github" in targets and cfg.external.github_token:
                    async def pub_github():
                        repo = github_repo
                        path = github_path or f"docs/openapi.yaml"
                        return await publisher.publish_to_github(spec, cfg.external.github_token, repo, path)
                    tasks.append(("GitHub", pub_github()))
                
                if "readme" in targets and cfg.external.readme_api_key:
                    async def pub_readme():
                        return await publisher.publish_to_readme(spec, cfg.external.readme_api_key, api_version)
                    tasks.append(("ReadMe", pub_readme()))
                
                for target_name, coro in tasks:
                    task = progress.add_task(f"Publishing to {target_name}...", total=None)
                    try:
                        result = await coro
                        results.append({"target": target_name, "success": True, "result": result})
                        progress.update(task, description=f"[green]✓ Published to {target_name}[/]")
                    except Exception as e:
                        results.append({"target": target_name, "success": False, "error": str(e)})
                        progress.update(task, description=f"[red]✗ Failed {target_name}: {e}[/]")
            
            asyncio.run(publish_all())
        
        table = Table(title="Publish Results")
        table.add_column("Target", style="cyan")
        table.add_column("Status")
        table.add_column("Details")
        for result in results:
            if result["success"]:
                table.add_row(result["target"], "[green]✓ Success[/]", str(result.get("result", {}).get("id", "")))
            else:
                table.add_row(result["target"], "[red]✗ Failed[/]", result["error"])
        console.print(table)
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if ctx.obj.get("debug"):
            console.print_exception()
        raise typer.Exit(1)
''')

write_file("apidoc_cli/commands/convert.py", r'''"""Convert command for OpenAPI specifications."""

import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from loguru import logger
from rich.console import Console

from apidoc_cli.utils import read_input, write_output

app = typer.Typer()
console = Console()


@app.command(name="convert")
def convert_command(
    ctx: typer.Context,
    input_file: Path = typer.Argument(..., help="Input specification file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    to_format: str = typer.Option("yaml", "--to", "-t", help="Output format (json/yaml)"),
    to_version: Optional[str] = typer.Option(None, "--version", "-v", help="Target OpenAPI version"),
    from_url: Optional[str] = typer.Option(None, "--from-url", help="Import from URL"),
    save: bool = typer.Option(False, "--save", help="Save to server"),
) -> None:
    """Convert between OpenAPI formats and versions."""
    
    debug = ctx.obj.get("debug", False)
    
    try:
        if from_url:
            import httpx
            console.print(f"[cyan]Fetching from URL:[/] {from_url}")
            response = httpx.get(from_url, timeout=30.0)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                spec = response.json()
            else:
                spec = yaml.safe_load(response.text)
        else:
            spec = read_input(input_file)
        
        if to_version:
            spec = _convert_version(spec, to_version)
            console.print(f"[green]✓[/] Converted to OpenAPI {to_version}")
        
        if not output:
            suffix = ".json" if to_format == "json" else ".yaml"
            output = input_file.with_suffix(suffix)
        
        write_output(spec, output, to_format)
        console.print(f"[green]✓[/] Saved to [bold]{output}[/]")
        
        if save:
            _save_to_server(ctx, spec)
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


def _convert_version(spec: dict, target_version: str) -> dict:
    current_version = spec.get("openapi") or spec.get("swagger")
    if not current_version:
        raise ValueError("Cannot detect OpenAPI version")
    
    if current_version.startswith("2.") and target_version.startswith("3."):
        return _swagger2_to_openapi3(spec)
    elif current_version.startswith("3.0") and target_version.startswith("3.1"):
        spec["openapi"] = "3.1.0"
        return spec
    elif current_version.startswith("3.1") and target_version.startswith("3.0"):
        spec["openapi"] = "3.0.3"
        return spec
    else:
        console.print(f"[yellow]Warning:[/] Version conversion may not be fully supported")
        return spec


def _swagger2_to_openapi3(spec: dict) -> dict:
    converted = {"openapi": "3.0.3", "info": spec.get("info", {}), "paths": {}, "components": {"schemas": {}, "parameters": {}, "responses": {}}}
    for path, methods in spec.get("paths", {}).items():
        converted["paths"][path] = {}
        for method, details in methods.items():
            if method not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                continue
            converted_method = details.copy()
            if "parameters" in details:
                converted_method["parameters"] = []
                for param in details["parameters"]:
                    if param.get("in") == "body":
                        converted_method["requestBody"] = {"content": {"application/json": {"schema": param.get("schema", {})}}}
                    else:
                        converted_method["parameters"].append(param)
            if "responses" in details:
                for status, response in details["responses"].items():
                    if "schema" in response:
                        response["content"] = {"application/json": {"schema": response.pop("schema")}}
            converted["paths"][path][method] = converted_method
    if "definitions" in spec:
        converted["components"]["schemas"] = spec["definitions"]
    return converted


def _save_to_server(ctx: typer.Context, spec: dict) -> None:
    import tempfile
    from apidoc_cli.commands.publish import publish_command
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(spec, f)
        temp_path = Path(f.name)
    try:
        ctx.invoke(publish_command, spec_file=temp_path, targets=["server"])
        console.print("[green]✓[/] Saved to server")
    finally:
        temp_path.unlink()
''')

write_file("apidoc_cli/commands/server.py", r'''"""Server management commands."""

import asyncio
import subprocess
import sys
from typing import Optional

import httpx
import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from apidoc_cli.config import Config

app = typer.Typer()
console = Console()


@app.command(name="start")
def server_start(
    ctx: typer.Context,
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of workers"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on changes"),
    background: bool = typer.Option(False, "--background", "-b", help="Run in background"),
) -> None:
    """Start APIDoc server."""
    
    try:
        if _is_server_running(host, port):
            console.print(f"[yellow]Server already running at http://{host}:{port}[/]")
            return
        
        cmd = [sys.executable, "-m", "uvicorn", "apidoc_server.main:app", "--host", host, "--port", str(port), "--workers", str(workers)]
        if reload:
            cmd.append("--reload")
        
        console.print(f"[green]Starting server at http://{host}:{port}[/]")
        
        if background:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            for _ in range(10):
                if _is_server_running(host, port):
                    console.print(f"[green]✓[/] Server started (PID: {process.pid})")
                    return
                asyncio.run(asyncio.sleep(0.5))
            console.print("[red]✗[/] Server failed to start")
        else:
            subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/]")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


@app.command(name="stop")
def server_stop(
    ctx: typer.Context,
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
) -> None:
    """Stop APIDoc server."""
    try:
        try:
            response = httpx.post(f"http://{host}:{port}/shutdown", timeout=5.0)
            if response.status_code == 200:
                console.print("[green]✓[/] Server stopped gracefully")
                return
        except Exception:
            pass
        console.print("[yellow]Could not stop gracefully, try manual termination[/]")
    except Exception as e:
        logger.error(f"Failed to stop server: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


@app.command(name="status")
def server_status(
    ctx: typer.Context,
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
) -> None:
    """Check server status."""
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            console.print(Panel(f"[green]✓ Server is running[/]\nURL: http://{host}:{port}\nVersion: {data.get('version', 'unknown')}", title="Server Status", border_style="green"))
        else:
            console.print("[red]✗ Server is not responding properly[/]")
            raise typer.Exit(1)
    except httpx.ConnectError:
        console.print("[yellow]Server is not running[/]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error checking server:[/] {e}")
        raise typer.Exit(1)


@app.command(name="search")
def server_search(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(20, "--limit", "-l", help="Results limit"),
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Server host"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Server port"),
) -> None:
    """Search specifications on server."""
    cfg: Config = ctx.obj["config"]
    server_url = f"http://{host or cfg.server.url.split('/')[2]}"
    try:
        response = httpx.get(f"{server_url}/api/v1/specs/search", params={"q": query, "per_page": limit}, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        if not data.get("items"):
            console.print(f"[yellow]No results found for '{query}'[/]")
            return
        table = Table(title=f"Search Results: '{query}'")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Version")
        table.add_column("Updated")
        for item in data["items"]:
            table.add_row(str(item["id"]), item["name"], item.get("version", "N/A"), item.get("updated_at", "N/A")[:10])
        console.print(table)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


@app.command(name="versions")
def server_versions(
    ctx: typer.Context,
    spec_id: int = typer.Argument(..., help="Specification ID"),
    host: Optional[str] = typer.Option(None, "--host", "-h"),
    port: Optional[int] = typer.Option(None, "--port", "-p"),
) -> None:
    """List versions of a specification."""
    cfg: Config = ctx.obj["config"]
    server_url = f"http://{host or cfg.server.url.split('/')[2]}"
    try:
        response = httpx.get(f"{server_url}/api/v1/specs/{spec_id}/versions", timeout=30.0)
        response.raise_for_status()
        data = response.json()
        table = Table(title=f"Versions for Specification #{spec_id}")
        table.add_column("Version", style="cyan")
        table.add_column("Created")
        table.add_column("Created By")
        table.add_column("Changelog")
        for version in data.get("items", []):
            table.add_row(version["version"], version["created_at"][:19], version.get("created_by", "N/A"), version.get("changelog", "")[:50])
        console.print(table)
    except Exception as e:
        logger.error(f"Failed to get versions: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


@app.command(name="init")
def server_init(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", "-f", help="Force reinitialize"),
) -> None:
    """Initialize server database."""
    try:
        from apidoc_server.database import init_db
        console.print("[cyan]Initializing database...[/]")
        asyncio.run(init_db())
        console.print("[green]✓[/] Database initialized")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)


def _is_server_running(host: str, port: int) -> bool:
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False
''')

write_file("apidoc_cli/commands/tree.py", r'''"""Tree visualization command."""

from pathlib import Path
from typing import Dict

import typer
from loguru import logger
from rich.console import Console
from rich.tree import Tree

from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


@app.command(name="tree")
def tree_command(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    show_methods: bool = typer.Option(True, "--methods/--no-methods", help="Show HTTP methods"),
    show_schemas: bool = typer.Option(False, "--schemas", help="Show schemas"),
    max_depth: int = typer.Option(10, "--depth", "-d", help="Maximum depth"),
) -> None:
    """Visualize API structure as tree."""
    
    try:
        spec = read_input(spec_file)
        title = spec.get("info", {}).get("title", "API")
        version = spec.get("info", {}).get("version", "")
        root = Tree(f"[bold cyan]{title}[/] [dim]v{version}[/]")
        
        paths = spec.get("paths", {})
        if paths:
            paths_branch = root.add("[bold green]Endpoints[/]")
            _add_paths(paths_branch, paths, show_methods)
        
        if show_schemas:
            schemas = spec.get("components", {}).get("schemas", {})
            if schemas:
                schemas_branch = root.add("[bold yellow]Schemas[/]")
                _add_schemas(schemas_branch, schemas)
        
        servers = spec.get("servers", [])
        if servers:
            servers_branch = root.add("[bold blue]Servers[/]")
            for server in servers:
                servers_branch.add(f"[dim]{server.get('url', '')}[/]")
        
        console.print(root)
    except Exception as e:
        logger.error(f"Tree visualization failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if ctx.obj.get("debug"):
            console.print_exception()
        raise typer.Exit(1)


def _add_paths(tree: Tree, paths: Dict, show_methods: bool) -> None:
    for path, methods in sorted(paths.items()):
        if not methods:
            continue
        path_branch = tree.add(f"[cyan]{path}[/]")
        if show_methods:
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                color = {"get": "green", "post": "yellow", "put": "blue", "delete": "red", "patch": "magenta"}.get(method.lower(), "white")
                method_text = f"[{color}]{method.upper()}[/]"
                if "summary" in details:
                    method_text += f" - [dim]{details['summary'][:50]}[/]"
                method_branch = path_branch.add(method_text)
                params = details.get("parameters", [])
                if params:
                    params_branch = method_branch.add("[dim]Parameters[/]")
                    for param in params:
                        required = "[red]*[/]" if param.get("required") else ""
                        params_branch.add(f"{param.get('name')} ({param.get('in')}) {required}")


def _add_schemas(tree: Tree, schemas: Dict) -> None:
    for name, schema in sorted(schemas.items()):
        schema_type = schema.get("type", "object")
        schema_branch = tree.add(f"[yellow]{name}[/] [dim]({schema_type})[/]")
        if schema_type == "object":
            props = schema.get("properties", {})
            for prop_name, prop_schema in list(props.items())[:10]:
                prop_type = prop_schema.get("type", "unknown")
                required = " [red]*[/]" if prop_name in schema.get("required", []) else ""
                schema_branch.add(f"[dim]{prop_name}: {prop_type}{required}[/]")
            if len(props) > 10:
                schema_branch.add(f"[dim]... and {len(props) - 10} more[/]")
''')

print("✓ CLI команды созданы (9 файлов)")
print()