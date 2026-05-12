"""Convert command for OpenAPI specifications."""

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


@app.callback()
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
            console.print(f"[green]OK[/] Converted to OpenAPI {to_version}")
        
        if not output:
            suffix = ".json" if to_format == "json" else ".yaml"
            output = input_file.with_suffix(suffix)
        
        write_output(spec, output, to_format)
        console.print(f"[green]OK[/] Saved to [bold]{output}[/]")
        
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
        console.print("[green]OK[/] Saved to server")
    finally:
        temp_path.unlink()
