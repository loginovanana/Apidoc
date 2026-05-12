"""APIDoc Manager CLI — main entry point."""
from __future__ import annotations
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from apidoc import __version__
from apidoc.config import setup_logging
from apidoc.utils.output import error, info, print_json, success, warning

console = Console()

app = typer.Typer(
    name="apidoc",
    help="[bold]APIDoc Manager CLI[/] — OpenAPI specification management tool.",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=True,
)
server_app = typer.Typer(help="Manage the APIDoc server and stored specs.")
app.add_typer(server_app, name="server")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold]apidoc[/] version [cyan]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[Optional[bool],
        typer.Option("--version", "-V", callback=_version_callback, is_eager=True)] = None,
) -> None:
    """APIDoc Manager CLI — automate your OpenAPI workflow."""


# ── generate ──────────────────────────────────────────────────────────────────
@app.command("generate")
def generate(
    source:      Annotated[Optional[Path], typer.Argument()] = None,
    output:      Annotated[Path, typer.Option("--output",    "-o")]  = Path("openapi.yaml"),
    fmt:         Annotated[str,  typer.Option("--format")]           = "yaml",
    framework:   Annotated[str,  typer.Option("--framework")]        = "auto",
    title:       Annotated[Optional[str], typer.Option("--title")]   = None,
    api_version: Annotated[str,  typer.Option("--version")]          = "1.0.0",
    interactive: Annotated[bool, typer.Option("--interactive", "-i")] = False,
    plugin:      Annotated[Optional[str], typer.Option("--plugin")]  = None,
    json_out:    Annotated[bool, typer.Option("--json")]             = False,
    debug:       Annotated[bool, typer.Option("--debug")]            = False,
) -> None:
    """Generate an OpenAPI specification from source code or interactively."""
    from loguru import logger
    from apidoc.plugins import GeneratorPlugin, load_plugins
    from apidoc.plugins.generators.fastapi_gen import FastAPIGeneratorPlugin
    from apidoc.plugins.generators.flask_gen import FlaskGeneratorPlugin
    from apidoc.utils.errors import PluginError
    from apidoc.utils.spec import save_spec

    BUILTIN = {"fastapi": FastAPIGeneratorPlugin, "flask": FlaskGeneratorPlugin}
    setup_logging(debug)

    if interactive:
        from apidoc.commands.generate import _interactive_wizard
        spec = _interactive_wizard()
        save_spec(spec, output, fmt)
        if json_out:
            print_json({"status": "ok", "output": str(output), "paths": len(spec.get("paths", {}))})
        else:
            success(f"Spec created → [bold]{output}[/]")
        return

    if source is None:
        error("Provide a SOURCE path or use --interactive", code="E008"); raise typer.Exit(1)
    if not source.exists():
        error(f"Source not found: {source}", code="E004"); raise typer.Exit(1)

    options = {"title": title or source.stem.title() + " API", "version": api_version}

    if plugin:
        try:
            gen_class = load_plugins("apidoc.generators").get(plugin)
            if not gen_class:
                error(f"Plugin '{plugin}' not found", code="E007"); raise typer.Exit(1)
        except PluginError as exc:
            error(exc.message, exc.detail, code=exc.code); raise typer.Exit(1)
    else:
        fw = framework
        if fw == "auto":
            text = ""
            if source.is_file(): text = source.read_text(errors="ignore")
            elif source.is_dir():
                for f in source.rglob("*.py"): text += f.read_text(errors="ignore")
            fw = ("fastapi" if ("from fastapi" in text or "FastAPI()" in text)
                  else "flask" if ("from flask" in text or "Flask(" in text)
                  else "fastapi")
            logger.debug(f"Auto-detected: {fw}")
        gen_class = BUILTIN.get(fw)
        if not gen_class:
            error(f"Unknown framework '{fw}'.", code="E007"); raise typer.Exit(1)

    try:
        if not json_out: info(f"Generating from [bold]{source}[/]…")
        spec = gen_class().generate(str(source), options)
    except Exception as exc:
        error(f"Generation failed: {exc}", code="E007")
        if debug: import traceback; traceback.print_exc()
        raise typer.Exit(1)

    save_spec(spec, output, fmt)
    n = len(spec.get("paths", {}))
    if json_out:
        print_json({"status": "ok", "output": str(output), "format": fmt, "framework": framework, "paths": n})
    else:
        success(f"Spec generated → [bold]{output}[/] ({n} endpoint(s))")


# ── validate ──────────────────────────────────────────────────────────────────
@app.command("validate")
def validate(
    spec_file:   Annotated[Path, typer.Argument()],
    fix:         Annotated[bool, typer.Option("--fix")]         = False,
    yes:         Annotated[bool, typer.Option("--yes", "-y")]   = False,
    strict:      Annotated[bool, typer.Option("--strict")]      = False,
    json_out:    Annotated[bool, typer.Option("--json")]        = False,
    debug:       Annotated[bool, typer.Option("--debug")]       = False,
    no_external: Annotated[bool, typer.Option("--no-external")] = False,
) -> None:
    """Validate an OpenAPI specification file."""
    from apidoc.api.validators import validate_external
    from apidoc.commands.validate import FIX_SUGGESTIONS, _run_local_validation
    from apidoc.utils.errors import NetworkError, ParseError
    from apidoc.utils.output import console
    from apidoc.utils.spec import load_spec, save_spec
    from rich.table import Table

    setup_logging(debug)
    try:
        spec = load_spec(spec_file)
    except FileNotFoundError:
        error(f"File not found: {spec_file}", code="E004"); raise typer.Exit(1)
    except ParseError as exc:
        error(exc.message, exc.detail, code=exc.code); raise typer.Exit(1)

    result: dict = {"file": str(spec_file), "valid": False,
                    "local_errors": [], "external_errors": [], "external_warnings": [],
                    "fixes_applied": []}

    if fix:
        applied: list[str] = []
        for sg in FIX_SUGGESTIONS:
            try:
                if sg["check"](spec):
                    if yes or typer.confirm(f"  Fix: {sg['message']} — {sg['hint']}?", default=True):
                        spec = sg["fix"](spec) or spec; applied.append(sg["message"])
            except Exception:
                pass
        if applied:
            save_spec(spec, spec_file); result["fixes_applied"] = applied
            if not json_out:
                for a in applied: success(f"Applied fix: {a}")

    result["local_errors"] = _run_local_validation(spec)
    if not no_external:
        try:
            ext = validate_external(spec)
            result["external_errors"]   = [e.get("message", str(e)) for e in ext.errors]
            result["external_warnings"] = [w.get("message", str(w)) for w in ext.warnings]
        except NetworkError as exc:
            if not json_out: warning(f"External validator unavailable: {exc.message} (skipped)")

    all_errors = result["local_errors"] + result["external_errors"]
    result["valid"] = len(all_errors) == 0 and (not strict or len(result["external_warnings"]) == 0)

    if json_out:
        print_json(result); raise typer.Exit(0 if result["valid"] else 1)

    if result["valid"]:
        success(f"[bold green]Spec is valid![/] ({spec_file})")
        for w in result["external_warnings"]: warning(f"Warning: {w}")
    else:
        error(f"Spec validation failed — {len(all_errors)} error(s)", code="E003")
        if result["local_errors"]:
            t = Table(title="Local Errors", header_style="bold red")
            t.add_column("#", style="dim", width=4); t.add_column("Error")
            for i, e in enumerate(result["local_errors"], 1): t.add_row(str(i), e)
            console.print(t)
        raise typer.Exit(1)


# ── diff ──────────────────────────────────────────────────────────────────────
@app.command("diff")
def diff(
    file1:        Annotated[Optional[Path], typer.Argument()] = None,
    file2:        Annotated[Optional[Path], typer.Argument()] = None,
    from_server:  Annotated[Optional[int], typer.Option("--from-server")]  = None,
    version1:     Annotated[Optional[str], typer.Option("--version1")]     = None,
    version2:     Annotated[Optional[str], typer.Option("--version2")]     = None,
    json_out:     Annotated[bool, typer.Option("--json")]                  = False,
    breaking_only:Annotated[bool, typer.Option("--breaking-only")]         = False,
    debug:        Annotated[bool, typer.Option("--debug")]                 = False,
) -> None:
    """Compare two versions of an OpenAPI specification."""
    from apidoc.api.client import ServerClient
    from apidoc.commands.diff import _compare_specs, _render_diff
    from apidoc.utils.errors import ApidocError
    from apidoc.utils.spec import load_spec

    setup_logging(debug)
    if from_server is not None:
        if not version1 or not version2:
            error("--version1 and --version2 required with --from-server", code="E008"); raise typer.Exit(1)
        try: diff_result = ServerClient().diff_versions(from_server, version1, version2)
        except ApidocError as exc:
            error(exc.message, exc.detail, code=exc.code); raise typer.Exit(1)
    else:
        if not file1 or not file2:
            error("Provide FILE1 and FILE2, or use --from-server", code="E008"); raise typer.Exit(1)
        try: diff_result = _compare_specs(load_spec(file1), load_spec(file2))
        except Exception as exc:
            error(f"Failed to load spec: {exc}", code="E004"); raise typer.Exit(1)

    if json_out: print_json(diff_result)
    else: _render_diff(diff_result, breaking_only)
    if diff_result["summary"]["breaking"] > 0: raise typer.Exit(1)


# ── mock ──────────────────────────────────────────────────────────────────────
@app.command("mock")
def mock(
    spec_file: Annotated[Path, typer.Argument()],
    port:      Annotated[int,          typer.Option("--port", "-p")] = 8080,
    host:      Annotated[str,          typer.Option("--host")]       = "localhost",
    log_file:  Annotated[Optional[Path], typer.Option("--log-file")] = None,
    delay:     Annotated[int,          typer.Option("--delay")]      = 0,
    debug:     Annotated[bool,         typer.Option("--debug")]      = False,
) -> None:
    """Run a mock server from an OpenAPI spec."""
    import uvicorn
    from apidoc.commands.mock import build_mock_app
    from apidoc.utils.errors import ParseError
    from apidoc.utils.spec import load_spec

    setup_logging(debug)
    try: spec = load_spec(spec_file)
    except (FileNotFoundError, ParseError) as exc:
        error(str(exc), code="E004"); raise typer.Exit(1)

    info(f"Loading [bold]{spec_file}[/] — {len(spec.get('paths', {}))} endpoint(s)")
    if log_file: info(f"Logging to [bold]{log_file}[/]")
    mock_app = build_mock_app(spec, log_file, delay)
    success(f"Mock server at [bold]http://{host}:{port}[/] — Ctrl+C to stop")
    uvicorn.run(mock_app, host=host, port=port, log_level="debug" if debug else "warning")


# ── testgen ───────────────────────────────────────────────────────────────────
@app.command("testgen")
def testgen(
    spec_file: Annotated[Path, typer.Argument()],
    framework: Annotated[str,          typer.Option("--framework")]  = "pytest",
    output:    Annotated[Path,         typer.Option("--output","-o")]= Path("tests/"),
    base_url:  Annotated[str,          typer.Option("--base-url")]   = "http://localhost:8000",
    plugin:    Annotated[Optional[str],typer.Option("--plugin")]     = None,
    json_out:  Annotated[bool,         typer.Option("--json")]       = False,
    debug:     Annotated[bool,         typer.Option("--debug")]      = False,
) -> None:
    """Generate tests from an OpenAPI specification."""
    from apidoc.plugins import TestGenPlugin, load_plugins
    from apidoc.plugins.testgens.pytest_gen import PytestTestGenPlugin
    from apidoc.utils.errors import PluginError
    from apidoc.utils.spec import load_spec

    BUILTIN = {"pytest": PytestTestGenPlugin}
    setup_logging(debug)
    try: spec = load_spec(spec_file)
    except Exception as exc:
        error(f"Failed to load spec: {exc}", code="E004"); raise typer.Exit(1)

    if plugin:
        try:
            gen_class = load_plugins("apidoc.testgens").get(plugin)
            if not gen_class: error(f"Plugin '{plugin}' not found", code="E007"); raise typer.Exit(1)
        except PluginError as exc:
            error(exc.message, exc.detail, code=exc.code); raise typer.Exit(1)
    else:
        gen_class = BUILTIN.get(framework)
        if not gen_class: error(f"Unknown framework '{framework}'.", code="E007"); raise typer.Exit(1)

    if not json_out: info(f"Generating [bold]{framework}[/] tests…")
    try: created = gen_class().generate(spec, str(output), base_url, {})
    except Exception as exc:
        error(f"Test generation failed: {exc}", code="E007"); raise typer.Exit(1)

    if json_out:
        print_json({"status": "ok", "framework": framework, "output_dir": str(output),
                    "files_created": created, "count": len(created)})
    else:
        success(f"Generated [bold]{len(created)}[/] file(s) in [bold]{output}[/]")
        for f in created: info(f"  [dim]{f}[/]")


# ── publish ───────────────────────────────────────────────────────────────────
@app.command("publish")
def publish(
    spec_file:   Annotated[Path, typer.Argument()],
    target:      Annotated[str,          typer.Option("--target")]      = "server",
    server_only: Annotated[bool,         typer.Option("--server-only")] = False,
    name:        Annotated[Optional[str],typer.Option("--name")]        = None,
    api_version: Annotated[Optional[str],typer.Option("--version")]     = None,
    changelog:   Annotated[str,          typer.Option("--changelog")]   = "",
    json_out:    Annotated[bool,         typer.Option("--json")]        = False,
    debug:       Annotated[bool,         typer.Option("--debug")]       = False,
) -> None:
    """Publish spec to own server and/or external services."""
    from apidoc.api.client import ServerClient
    from apidoc.api.publishers import PUBLISHERS
    from apidoc.utils.errors import ApidocError
    from apidoc.utils.output import console
    from apidoc.utils.spec import detect_format, load_spec, spec_to_str
    from rich.table import Table

    ALL_TARGETS = {"swaggerhub", "github", "gitlab", "redocly", "readme"}
    setup_logging(debug)
    try: spec = load_spec(spec_file)
    except Exception as exc:
        error(f"Cannot load spec: {exc}", code="E004"); raise typer.Exit(1)

    spec_name    = name or spec.get("info", {}).get("title", spec_file.stem)
    spec_version = api_version or spec.get("info", {}).get("version", "1.0.0")
    spec_content = spec_to_str(spec, detect_format(spec_file))
    targets: set[str] = set()
    if not server_only:
        raw = target.strip().lower()
        if raw == "all": targets = ALL_TARGETS.copy()
        elif raw and raw != "server": targets = {t.strip() for t in raw.split(",") if t.strip()}

    results: list[dict] = []
    if not json_out: info("Publishing to own server…")
    try:
        sc = ServerClient(); srv = sc.create_spec(spec_name, spec, "")
        spec_id = srv.get("id")
        if spec_id:
            try: sc.create_version(spec_id, spec_version, spec, changelog)
            except Exception: pass
        results.append({"service": "server", "status": "published",
                        "id": spec_id, "name": spec_name, "version": spec_version})
        if not json_out: success(f"Server: published [bold]{spec_name}[/] v{spec_version}")
    except ApidocError as exc:
        results.append({"service": "server", "status": "error", "error": exc.message})
        if not json_out: error(f"Server: {exc.message}", exc.detail, code=exc.code)

    for svc in sorted(targets):
        if svc not in PUBLISHERS: continue
        if not json_out: info(f"Publishing to {svc}…")
        try:
            fn = PUBLISHERS[svc]
            if svc == "swaggerhub": res = fn(spec, spec_name, spec_version)
            elif svc in ("github", "gitlab", "readme"): res = fn(spec_content)
            else: res = fn(spec, spec_name)
            results.append(res)
            if not json_out: success(f"{svc}: published")
        except ApidocError as exc:
            results.append({"service": svc, "status": "error", "error": exc.message})
            if not json_out: error(f"{svc}: {exc.message}", code=exc.code)
        except Exception as exc:
            results.append({"service": svc, "status": "error", "error": str(exc)})
            if debug: import traceback; traceback.print_exc()

    if json_out:
        print_json({"results": results,
                    "summary": {"published": sum(1 for r in results if r.get("status") == "published"),
                                "errors": sum(1 for r in results if r.get("status") == "error")}})
    else:
        t = Table(title="Publish Results", header_style="bold blue")
        t.add_column("Service"); t.add_column("Status"); t.add_column("Details")
        for r in results:
            s = r.get("status","?")
            t.add_row(r.get("service","?"),
                      f"[green]{s}[/]" if s=="published" else f"[red]{s}[/]",
                      str(r.get("url") or r.get("error") or ""))
        console.print(t)


# ── convert ───────────────────────────────────────────────────────────────────
@app.command("convert")
def convert(
    input_file:      Annotated[Optional[Path], typer.Argument()] = None,
    to:              Annotated[Optional[str],  typer.Option("--to")]               = None,
    output:          Annotated[Path,           typer.Option("--output", "-o")]     = Path("converted.yaml"),
    from_url:        Annotated[Optional[str],  typer.Option("--from-url")]         = None,
    from_swaggerhub: Annotated[Optional[str],  typer.Option("--from-swaggerhub")]  = None,
    from_github:     Annotated[Optional[str],  typer.Option("--from-github")]      = None,
    json_out:        Annotated[bool,           typer.Option("--json")]             = False,
    debug:           Annotated[bool,           typer.Option("--debug")]            = False,
) -> None:
    """Convert OpenAPI specs between formats/versions or import from external sources."""
    from apidoc.commands.convert import (_fetch_from_github, _fetch_from_swaggerhub,
                                          _fetch_from_url, _openapi30_to_swagger2)
    from apidoc.utils.spec import load_spec, save_spec

    setup_logging(debug)
    if to is None and not any([from_url, from_swaggerhub, from_github]):
        error("Specify --to or an import source", code="E008"); raise typer.Exit(1)

    try:
        if from_url:
            if not json_out: info(f"Importing from URL: {from_url}")
            spec = _fetch_from_url(from_url)
        elif from_swaggerhub: spec = _fetch_from_swaggerhub(from_swaggerhub)
        elif from_github:     spec = _fetch_from_github(from_github)
        elif input_file:      spec = load_spec(input_file)
        else:
            error("No input specified", code="E008"); raise typer.Exit(1)
    except Exception as exc:
        error(f"Import/load failed: {exc}", code="E001"); raise typer.Exit(1)

    operations: list[str] = []
    if to == "swagger2":
        spec = _openapi30_to_swagger2(spec); operations.append("openapi3→swagger2")
    elif to in ("openapi3.0", "openapi3.1"):
        target_ver = "3.0.3" if to == "openapi3.0" else "3.1.0"
        spec["openapi"] = target_ver; operations.append(f"set openapi={target_ver}")

    out_fmt = "json" if (to == "json" or str(output).endswith(".json")) else "yaml"
    save_spec(spec, output, out_fmt)

    if json_out:
        print_json({"status": "ok", "output": str(output), "format": out_fmt,
                    "operations": operations, "paths": len(spec.get("paths", {}))})
    else:
        success(f"Converted → [bold]{output}[/]")


# ── tree ──────────────────────────────────────────────────────────────────────
@app.command("tree")
def tree(
    spec_file: Annotated[Path, typer.Argument()],
    depth:     Annotated[int,  typer.Option("--depth")] = 0,
    json_out:  Annotated[bool, typer.Option("--json")]  = False,
    debug:     Annotated[bool, typer.Option("--debug")] = False,
) -> None:
    """Visualize API structure as an ASCII tree."""
    from apidoc.commands.tree import METHOD_COLORS, spec_to_tree_dict
    from apidoc.utils.output import console
    from apidoc.utils.spec import load_spec
    from rich.tree import Tree

    setup_logging(debug)
    try: spec = load_spec(spec_file)
    except Exception as exc:
        error(f"Cannot load spec: {exc}", code="E004"); raise typer.Exit(1)

    if json_out:
        print_json(spec_to_tree_dict(spec)); return

    info_block = spec.get("info", {}); paths = spec.get("paths", {})
    title = info_block.get("title", "API"); version = info_block.get("version", "?")
    root = Tree(f"[bold cyan]{title}[/] [dim]v{version}[/]")
    path_tree: dict = {}
    for path_str, path_item in paths.items():
        parts = [p for p in path_str.strip("/").split("/") if p] or ["(root)"]
        current = path_tree
        for i, part in enumerate(parts):
            if depth > 0 and i >= depth: break
            if part not in current: current[part] = {"__children__": {}, "__ops__": []}
            if i == len(parts) - 1:
                for method, op in path_item.items():
                    if method.upper() in METHOD_COLORS and isinstance(op, dict):
                        current[part]["__ops__"].append(
                            {"method": method.upper(), "summary": op.get("summary", "")})
            current = current[part]["__children__"]

    def _add_nodes(branch: Tree, subtree: dict, prefix: str = "/") -> None:
        for segment, content in subtree.items():
            if segment in ("__children__", "__ops__"): continue
            fp = f"{prefix.rstrip('/')}/{segment}"
            nb = branch.add(f"[white]{fp}[/]")
            for op in content.get("__ops__", []):
                m = op["method"]; color = METHOD_COLORS.get(m, "white")
                ss = f"  [dim]{op['summary']}[/]" if op["summary"] else ""
                nb.add(f"[{color}]{m:<8}[/]{ss}")
            _add_nodes(nb, content.get("__children__", {}), fp)

    _add_nodes(root, path_tree)
    n_ops = sum(1 for pi in paths.values() for m in pi if m.upper() in METHOD_COLORS)
    root.add(f"\n[dim]{len(paths)} paths · {n_ops} operations[/]")
    console.print(root)


# ── server sub-commands ───────────────────────────────────────────────────────
from apidoc.commands.server import (
    server_delete, server_get, server_init, server_list,
    server_search, server_start, server_status, server_stop, server_versions,
)
server_app.command("start")(server_start)
server_app.command("stop")(server_stop)
server_app.command("status")(server_status)
server_app.command("init")(server_init)
server_app.command("list")(server_list)
server_app.command("get")(server_get)
server_app.command("search")(server_search)
server_app.command("versions")(server_versions)
server_app.command("delete")(server_delete)

if __name__ == "__main__":
    app()
