"""Server sub-command functions."""
from __future__ import annotations
import os, signal
from pathlib import Path
from typing import Annotated, Optional
import typer
from loguru import logger
from rich.table import Table
from apidoc.api.client import ServerClient
from apidoc.config import DATA_DIR, LOG_DIR, setup_logging
from apidoc.utils.errors import ApidocError, NetworkError
from apidoc.utils.output import console, error, info, print_json, success, warning

PID_FILE = DATA_DIR / "server.pid"

def server_start(
    port: Annotated[int, typer.Option("--port")] = 8000,
    host: Annotated[str, typer.Option("--host")] = "localhost",
    log_file: Annotated[Optional[Path], typer.Option("--log-file")] = None,
    db_url:   Annotated[Optional[str],  typer.Option("--db-url")]   = None,
    reload:   Annotated[bool, typer.Option("--reload")] = False,
    daemon:   Annotated[bool, typer.Option("--daemon")] = False,
    debug:    Annotated[bool, typer.Option("--debug")]  = False,
) -> None:
    """Start the APIDoc REST API server."""
    setup_logging(debug)
    if db_url: os.environ["APIDOC_DB_URL"] = db_url
    _log = log_file or (LOG_DIR / "server.log"); os.environ["APIDOC_SERVER_LOG"] = str(_log)
    if daemon and hasattr(os,"fork"):
        pid = os.fork()
        if pid > 0:
            PID_FILE.write_text(str(pid))
            success(f"Server started (PID {pid}). Stop: apidoc server stop"); return
    elif daemon: warning("--daemon requires Unix. Starting in foreground.")
    import uvicorn
    info(f"Starting server at [bold]http://{host}:{port}[/]")
    info(f"Docs: http://{host}:{port}/docs  |  Logs: {_log}"); info("Ctrl+C to stop\n")
    uvicorn.run("server.main:app", host=host, port=port, reload=reload,
                log_level="debug" if debug else "info")

def server_stop() -> None:
    """Stop a daemonised server."""
    if not PID_FILE.exists(): warning("No PID file found."); return
    pid = int(PID_FILE.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM); PID_FILE.unlink(missing_ok=True); success(f"Server (PID {pid}) stopped.")
    except ProcessLookupError: warning(f"Process {pid} not found."); PID_FILE.unlink(missing_ok=True)
    except PermissionError: error(f"No permission to stop PID {pid}", code="E008")

def server_status(json_out: Annotated[bool, typer.Option("--json")] = False) -> None:
    """Check server health."""
    sc = ServerClient()
    try:
        result = {**sc.health(), **sc.info(), "reachable": True}
        if json_out: print_json(result)
        else:
            success(f"Server is [bold green]online[/] at {sc.base_url}")
            for k,v in result.items():
                if k != "reachable": info(f"  [dim]{k}:[/] {v}")
    except NetworkError as exc:
        result = {"reachable": False, "error": exc.message}
        if json_out: print_json(result)
        else: error(f"Server offline: {exc.message}", "Run: apidoc server start", code="E001")
        raise typer.Exit(1)

def server_init(debug: Annotated[bool, typer.Option("--debug")] = False) -> None:
    """Initialise DB with Alembic migrations."""
    setup_logging(debug)
    try:
        from alembic import command as ac; from alembic.config import Config as AC
        cfg = AC(); migrations_dir = Path(__file__).parent.parent.parent / "server" / "migrations"
        cfg.set_main_option("script_location", str(migrations_dir))
        cfg.set_main_option("sqlalchemy.url",
            os.environ.get("APIDOC_DB_URL", f"sqlite:///{DATA_DIR / 'apidoc.db'}")
                .replace("+aiosqlite",""))
        ac.upgrade(cfg, "head"); success("Database initialised.")
    except Exception as exc:
        error(f"DB init failed: {exc}", code="E006")
        if debug: import traceback; traceback.print_exc()
        raise typer.Exit(1)

def server_list(
    page:     Annotated[int,  typer.Option("--page",  "-p")] = 1,
    limit:    Annotated[int,  typer.Option("--limit", "-l")] = 20,
    json_out: Annotated[bool, typer.Option("--json")]        = False,
    debug:    Annotated[bool, typer.Option("--debug")]       = False,
) -> None:
    """List stored specifications."""
    setup_logging(debug)
    try: data = ServerClient().list_specs(page=page, limit=limit)
    except ApidocError as exc: error(exc.message, exc.detail, code=exc.code); raise typer.Exit(1)
    if json_out: print_json(data); return
    items = data.get("items", data) if isinstance(data, dict) else data
    if not items: info("No specs found."); return
    t = Table(title=f"Stored Specs (page {page})", header_style="bold magenta")
    for col in ("ID","Name","Latest Version","Versions","Updated"): t.add_column(col)
    for i in items:
        t.add_row(str(i.get("id","")), i.get("name",""), i.get("latest_version",""),
                  str(i.get("versions_count","")), str(i.get("updated_at",""))[:19])
    console.print(t)

def server_get(
    spec_id:  Annotated[int,  typer.Argument(help="Spec ID")],
    json_out: Annotated[bool, typer.Option("--json")]    = False,
    fmt:      Annotated[str,  typer.Option("--format")]  = "yaml",
    debug:    Annotated[bool, typer.Option("--debug")]   = False,
) -> None:
    """Retrieve a spec by ID."""
    setup_logging(debug)
    try: data = ServerClient().get_spec(spec_id)
    except ApidocError as exc: error(exc.message, exc.detail, code=exc.code); raise typer.Exit(1)
    if json_out: print_json(data); return
    info(f"[bold]{data.get('name')}[/] (id={spec_id})")
    content = data.get("content") or data
    if fmt == "json": import json as _j; console.print(_j.dumps(content, indent=2))
    else: import yaml; console.print(yaml.dump(content, allow_unicode=True))

def server_search(
    query:    Annotated[str,  typer.Argument(help="Search query")],
    page:     Annotated[int,  typer.Option("--page")]  = 1,
    limit:    Annotated[int,  typer.Option("--limit")] = 10,
    json_out: Annotated[bool, typer.Option("--json")]  = False,
    debug:    Annotated[bool, typer.Option("--debug")] = False,
) -> None:
    """Search specs by name or description."""
    setup_logging(debug)
    try: data = ServerClient().search_specs(query, page=page, limit=limit)
    except ApidocError as exc: error(exc.message, exc.detail, code=exc.code); raise typer.Exit(1)
    if json_out: print_json(data); return
    items = data.get("items", data) if isinstance(data,dict) else data
    if not items: info(f"No specs matching '{query}'."); return
    t = Table(title=f"Search: '{query}'", header_style="bold magenta")
    for col in ("ID","Name","Latest Version","Updated"): t.add_column(col)
    for i in items:
        t.add_row(str(i.get("id","")), i.get("name",""), i.get("latest_version",""),
                  str(i.get("updated_at",""))[:19])
    console.print(t)

def server_versions(
    spec_id:  Annotated[int,  typer.Argument(help="Spec ID")],
    json_out: Annotated[bool, typer.Option("--json")]  = False,
    debug:    Annotated[bool, typer.Option("--debug")] = False,
) -> None:
    """Show version history."""
    setup_logging(debug)
    try: data = ServerClient().list_versions(spec_id)
    except ApidocError as exc: error(exc.message, exc.detail, code=exc.code); raise typer.Exit(1)
    if json_out: print_json(data); return
    items = data.get("items", data) if isinstance(data,dict) else data
    if not items: info(f"No versions for spec {spec_id}."); return
    t = Table(title=f"Version History — Spec #{spec_id}", header_style="bold magenta")
    for col in ("Version","Created","Changelog"): t.add_column(col)
    for i in items:
        t.add_row(i.get("version",""), str(i.get("created_at",""))[:19],
                  i.get("changelog","") or "[dim]—[/]")
    console.print(t)

def server_delete(
    spec_id:  Annotated[int,  typer.Argument(help="Spec ID")],
    yes:      Annotated[bool, typer.Option("--yes", "-y")] = False,
    json_out: Annotated[bool, typer.Option("--json")]      = False,
    debug:    Annotated[bool, typer.Option("--debug")]     = False,
) -> None:
    """Delete a spec from the server."""
    setup_logging(debug)
    if not yes: typer.confirm(f"Delete spec #{spec_id}?", abort=True)
    try: data = ServerClient().delete_spec(spec_id)
    except ApidocError as exc: error(exc.message, exc.detail, code=exc.code); raise typer.Exit(1)
    if json_out: print_json({"deleted": spec_id, **data})
    else: success(f"Spec #{spec_id} deleted.")
