"""Validate OpenAPI specifications."""

from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from apidoc_cli.validators import OpenAPIValidator

app = typer.Typer()
console = Console()


@app.callback()
def validate(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Strict validation mode"),
    remote: bool = typer.Option(False, "--remote", help="Use remote validator API"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix common issues"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
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
            console.print(Panel("[bold green]OK Specification is valid![/]", border_style="green"))
            if results.get("warnings"):
                console.print("\n[yellow]Warnings:[/]")
                for warning in results["warnings"]:
                    console.print(f"  * {warning}")
        else:
            console.print(Panel("[bold red]FAIL Specification has errors[/]", border_style="red"))
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
                            console.print(f"  [green]OK[/] Fixed: {issue['description']}")
                        else:
                            console.print(f"  [red]FAIL[/] Failed to fix: {issue['description']}")
            raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if debug:
            console.print_exception()
        raise typer.Exit(1)
