"""Generate OpenAPI specifications from source code."""

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


@app.callback()
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
                progress.update(task, description="[green]OK[/] Parsing complete")
            except Exception as e:
                progress.update(task, description="[red]FAIL[/] Parsing failed")
                logger.error(f"Failed to parse source: {e}")
                if debug:
                    console.print_exception()
                raise typer.Exit(1)
    
    output_path = output or Path(f"openapi.{format}")
    write_output(spec, output_path, format)
    
    if not ctx.obj.get("json_output"):
        _show_preview(spec)
    
    console.print(f"\n[green]OK[/] Specification saved to [bold]{output_path}[/]")


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
        console.print(f"  [green]OK[/] Added {method} {path}")
    
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
