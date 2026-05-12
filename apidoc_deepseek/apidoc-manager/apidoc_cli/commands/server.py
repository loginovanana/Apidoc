"""Server management commands."""

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
                    console.print(f"[green]OK[/] Server started (PID: {process.pid})")
                    return
                asyncio.run(asyncio.sleep(0.5))
            console.print("[red]FAIL[/] Server failed to start")
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
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Server host"),
    port: int = typer.Option(8000, "--port", "-p", help="Server port"),
) -> None:
    """Stop APIDoc server."""
    try:
        try:
            response = httpx.post(f"http://{host}:{port}/shutdown", timeout=5.0)
            if response.status_code == 200:
                console.print("[green]OK[/] Server stopped gracefully")
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
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Server host"),
    port: int = typer.Option(8000, "--port", "-p", help="Server port"),
) -> None:
    """Check server status."""
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            console.print(Panel(f"[green]OK Server is running[/]\nURL: http://{host}:{port}\nVersion: {data.get('version', 'unknown')}", title="Server Status", border_style="green"))
        else:
            console.print("[red]FAIL Server is not responding properly[/]")
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
    host: Optional[str] = typer.Option("127.0.0.1", "--host", "-h", help="Server host"),
    port: Optional[int] = typer.Option(8000, "--port", "-p", help="Server port"),
) -> None:
    """Search specifications on server."""
    server_url = f"http://{host}:{port}"
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
    host: Optional[str] = typer.Option("127.0.0.1", "--host", "-h", help="Server host"),
    port: Optional[int] = typer.Option(8000, "--port", "-p", help="Server port"),
) -> None:
    """List versions of a specification."""
    server_url = f"http://{host}:{port}"
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
        console.print("[green]OK[/] Database initialized")
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