"""Custom exceptions and error handling for APIDoc CLI."""

import sys
from typing import Optional

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.traceback import Traceback

console = Console()


class APIDocError(Exception):
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[dict] = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(message)


class ValidationError(APIDocError):
    def __init__(self, message: str, errors: list = None):
        super().__init__(message, code="VALIDATION_ERROR", details={"errors": errors or []})


class NetworkError(APIDocError):
    def __init__(self, message: str, url: str, status_code: Optional[int] = None):
        super().__init__(message, code="NETWORK_ERROR", details={"url": url, "status_code": status_code})


class ConfigurationError(APIDocError):
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, code="CONFIG_ERROR", details={"config_key": config_key})


class PluginError(APIDocError):
    def __init__(self, message: str, plugin_name: str):
        super().__init__(message, code="PLUGIN_ERROR", details={"plugin": plugin_name})


class ParseError(APIDocError):
    def __init__(self, message: str, file_path: str, line: Optional[int] = None):
        super().__init__(message, code="PARSE_ERROR", details={"file": file_path, "line": line})


class AuthenticationError(APIDocError):
    def __init__(self, message: str, service: str):
        super().__init__(message, code="AUTH_ERROR", details={"service": service})


def handle_error(error: Exception, debug: bool = False, exit_on_error: bool = True) -> None:
    if isinstance(error, APIDocError):
        _handle_apidoc_error(error, debug)
    else:
        _handle_unexpected_error(error, debug)
    if exit_on_error:
        sys.exit(1)


def _handle_apidoc_error(error: APIDocError, debug: bool) -> None:
    error_colors = {
        "VALIDATION_ERROR": "yellow", "NETWORK_ERROR": "red", "CONFIG_ERROR": "yellow",
        "PLUGIN_ERROR": "magenta", "PARSE_ERROR": "yellow", "AUTH_ERROR": "red",
    }
    color = error_colors.get(error.code, "red")
    console.print(Panel(f"[bold {color}]{error.code}[/]\n{error.message}", title="Error", border_style=color))
    if error.details and debug:
        console.print("\n[dim]Details:[/]")
        for key, value in error.details.items():
            console.print(f"  {key}: {value}")
    logger.error(f"{error.code}: {error.message}", **error.details)


def _handle_unexpected_error(error: Exception, debug: bool) -> None:
    if debug:
        console.print(Traceback.from_exception(type(error), error, error.__traceback__, show_locals=True))
    else:
        console.print(Panel(f"[red]An unexpected error occurred:[/]\n{str(error)}", title="Unexpected Error", border_style="red"))
        console.print("\n[dim]Run with --debug for more details[/]")
    logger.exception("Unexpected error occurred")
