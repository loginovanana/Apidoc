"""Tree visualization command."""

from pathlib import Path
from typing import Dict

import typer
from loguru import logger
from rich.console import Console
from rich.tree import Tree

from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


@app.callback()
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
