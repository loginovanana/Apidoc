"""HTTP client for the APIDoc REST API server."""
from __future__ import annotations
from typing import Any, Optional
import httpx
from loguru import logger
from apidoc.config import settings
from apidoc.utils.errors import AuthError, NetworkError, NotFoundError, ServerError

class ServerClient:
    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        self.base_url = (base_url or settings.server_url).rstrip("/")
        self.timeout  = timeout or settings.server_timeout

    def _handle(self, resp: httpx.Response) -> dict[str, Any]:
        logger.debug(f"← {resp.status_code} {resp.url}")
        if resp.status_code == 401: raise AuthError("Authentication failed")
        if resp.status_code == 404: raise NotFoundError("Resource not found (404)")
        if resp.status_code >= 500: raise ServerError(f"Server error {resp.status_code}", resp.text[:200])
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    def _get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        try:
            logger.debug(f"→ GET {self.base_url}{path}")
            return self._handle(httpx.get(f"{self.base_url}{path}", params=params, timeout=self.timeout))
        except httpx.ConnectError as e:
            raise NetworkError(f"Cannot connect to {self.base_url}","Run: apidoc server start") from e
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out ({self.timeout}s)") from e

    def _post(self, path: str, data: Any = None) -> dict[str, Any]:
        try:
            logger.debug(f"→ POST {self.base_url}{path}")
            return self._handle(httpx.post(f"{self.base_url}{path}", json=data, timeout=self.timeout))
        except httpx.ConnectError as e:
            raise NetworkError(f"Cannot connect to {self.base_url}","Run: apidoc server start") from e
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out ({self.timeout}s)") from e

    def _delete(self, path: str) -> dict[str, Any]:
        try:
            return self._handle(httpx.delete(f"{self.base_url}{path}", timeout=self.timeout))
        except httpx.ConnectError as e:
            raise NetworkError(f"Cannot connect to {self.base_url}") from e

    def list_specs(self, page: int = 1, limit: int = 20) -> dict:
        return self._get("/specs", params={"page": page, "limit": limit})
    def get_spec(self, spec_id: int) -> dict:
        return self._get(f"/specs/{spec_id}")
    def create_spec(self, name: str, content: dict, description: str = "") -> dict:
        return self._post("/specs", data={"name": name, "description": description, "content": content})
    def delete_spec(self, spec_id: int) -> dict:
        return self._delete(f"/specs/{spec_id}")
    def search_specs(self, query: str, page: int = 1, limit: int = 10) -> dict:
        return self._get("/specs/search", params={"q": query, "page": page, "limit": limit})
    def import_spec(self, url: str) -> dict:
        return self._post("/specs/import", data={"url": url})
    def list_versions(self, spec_id: int) -> dict:
        return self._get(f"/specs/{spec_id}/versions")
    def create_version(self, spec_id: int, version: str, content: dict, changelog: str = "") -> dict:
        return self._post(f"/specs/{spec_id}/versions",
                          data={"version": version, "content": content, "changelog": changelog})
    def diff_versions(self, spec_id: int, version1: str, version2: str) -> dict:
        return self._post(f"/specs/{spec_id}/diff", data={"version1": version1, "version2": version2})
    def health(self) -> dict: return self._get("/health")
    def info(self)   -> dict: return self._get("/info")

client = ServerClient()
