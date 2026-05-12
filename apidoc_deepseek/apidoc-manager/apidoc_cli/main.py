#!/usr/bin/env python3
"""APIDoc Manager CLI - Main entry point."""

from pathlib import Path
from typing import Optional

import sys
import typer
from loguru import logger
from rich.console import Console

from apidoc_cli import get_logo
from apidoc_cli.config import Config, setup_logging
from apidoc_cli.utils import get_version

# Импортируем конкретные функции команд из модулей
from apidoc_cli.commands.validate import validate
from apidoc_cli.commands.tree import tree_command
from apidoc_cli.commands.diff import diff_command
from apidoc_cli.commands.mock import mock_command
from apidoc_cli.commands.testgen import testgen_command
from apidoc_cli.commands.publish import publish_command
from apidoc_cli.commands.convert import convert_command
from apidoc_cli.commands.generate import generate

# server оставляем как группу
import apidoc_cli.commands.server as server_mod

if sys.stdout.encoding.upper() != "UTF-8":
    sys.stdout.reconfigure(encoding="utf-8")

app = typer.Typer(
    name="apidoc",
    help="APIDoc Manager - OpenAPI specification automation toolkit",
    add_completion=True,
    rich_markup_mode="rich",
)

console = Console()

# Регистрируем команды напрямую
app.command(name="generate", help="Generate OpenAPI specs from source code")(generate)
app.command(name="validate", help="Validate OpenAPI specifications")(validate)
app.command(name="diff", help="Compare two OpenAPI specifications")(diff_command)
app.command(name="mock", help="Start mock server from specification")(mock_command)
app.command(name="testgen", help="Generate tests from specification")(testgen_command)
app.command(name="publish", help="Publish specification to services")(publish_command)
app.command(name="convert", help="Convert between formats and versions")(convert_command)
app.command(name="tree", help="Visualize API structure")(tree_command)

# server – с подкомандами
app.add_typer(server_mod.app, name="server", help="Manage APIDoc server")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config file"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    log_file: Optional[Path] = typer.Option(None, "--log-file", help="Path to log file"),
    version: bool = typer.Option(False, "--version", help="Show version", is_eager=True),
) -> None:
    """APIDoc Manager - OpenAPI specification automation toolkit."""
    
    if version:
        console.print(f"[bold green]APIDoc Manager[/] version {get_version()}")
        raise typer.Exit()
    
    if not ctx.invoked_subcommand:
        console.print(get_logo())
    
    setup_logging(debug=debug, log_file=log_file)
    cfg = Config.load(config)
    
    ctx.obj = {"config": cfg, "debug": debug, "json_output": json_output}
    
    if debug:
        logger.debug("Debug mode enabled")
        console.print("[yellow]Warning: Debug mode enabled[/]")


if __name__ == "__main__":
    app()