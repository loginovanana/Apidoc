"""Rich output helpers."""
from __future__ import annotations
import json, sys, traceback
from typing import Any
import yaml
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console     = Console()
err_console = Console(stderr=True)

def success(msg: str) -> None: console.print(f"[bold green]✓[/] {msg}")
def info(msg: str)    -> None: console.print(f"[bold cyan]ℹ[/] {msg}")
def warning(msg: str) -> None: console.print(f"[bold yellow]⚠[/] {msg}")
def error(msg: str, detail: str = "", code: str = "") -> None:
    label = f"[bold red][{code}][/] " if code else ""
    err_console.print(f"{label}[bold red]✗[/] {msg}")
    if detail: err_console.print(f"  [dim]{detail}[/]")

def print_json(data: Any) -> None:
    raw = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    console.print(Syntax(raw, "json", theme="monokai", word_wrap=True))

def fatal(msg: str, detail: str = "", code: str = "", debug: bool = False,
          exc: BaseException | None = None) -> None:
    error(msg, detail, code)
    if debug and exc: err_console.print(traceback.format_exc())
    sys.exit(1)

def make_table(*columns: str, title: str = "") -> Table:
    t = Table(title=title, show_header=True, header_style="bold magenta")
    for col in columns: t.add_column(col)
    return t
