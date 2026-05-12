"""API routes module."""

from apidoc_server.api import auth, diff, import_export, search, specs, versions

__all__ = ["specs", "versions", "diff", "search", "import_export", "auth"]
