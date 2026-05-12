"""Compare OpenAPI specifications."""

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


@app.callback()
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
