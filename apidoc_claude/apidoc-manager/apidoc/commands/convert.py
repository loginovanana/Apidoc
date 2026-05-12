"""Convert command helpers."""
from __future__ import annotations
import json
from typing import Any
from urllib.parse import urlparse
import httpx, yaml
from loguru import logger
from apidoc.config import settings
from apidoc.utils.errors import NetworkError

def _fetch_from_url(url: str) -> dict[str, Any]:
    logger.debug(f"→ GET {url}")
    try:
        r = httpx.get(url, timeout=30, follow_redirects=True); r.raise_for_status()
    except httpx.ConnectError as e: raise NetworkError(f"Cannot reach {url}") from e
    except httpx.HTTPStatusError as e: raise NetworkError(f"HTTP {e.response.status_code}") from e
    ct = r.headers.get("content-type","")
    return json.loads(r.text) if ("json" in ct or url.endswith(".json")) else yaml.safe_load(r.text)

def _fetch_from_swaggerhub(ref: str) -> dict[str, Any]:
    parts = ref.split("/")
    if len(parts) != 3: raise ValueError("Must be owner/api/version")
    owner, api, ver = parts
    url = f"https://api.swaggerhub.com/apis/{owner}/{api}/{ver}"
    hdrs = {}
    if settings.swaggerhub_token: hdrs["Authorization"] = settings.swaggerhub_token
    try:
        r = httpx.get(url, headers=hdrs, timeout=30); r.raise_for_status(); return r.json()
    except httpx.ConnectError as e: raise NetworkError("Cannot reach SwaggerHub") from e

def _fetch_from_github(ref: str) -> dict[str, Any]:
    import re
    m = re.match(r"([^/]+)/([^/]+)/(.+?)(?:@(.+))?$", ref)
    if not m: raise ValueError("Must be owner/repo/path[@branch]")
    owner, repo, path, branch = m.groups()
    return _fetch_from_url(
        f"https://raw.githubusercontent.com/{owner}/{repo}/{branch or 'main'}/{path}")

def _openapi30_to_swagger2(spec: dict[str, Any]) -> dict[str, Any]:
    parsed = urlparse((spec.get("servers",[{}]) or [{}])[0].get("url","http://localhost"))
    sw: dict[str, Any] = {"swagger":"2.0","info":spec.get("info",{}),"paths":{},
                           "host":parsed.netloc or "localhost","basePath":parsed.path or "/",
                           "schemes":[parsed.scheme or "https"]}
    for path_str, pi in spec.get("paths",{}).items():
        sw["paths"][path_str] = {}
        for m, op in pi.items():
            if m.upper() not in ("GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"): continue
            nop: dict[str, Any] = {
                "operationId": op.get("operationId",f"{m}_{path_str}"),
                "summary": op.get("summary",""), "description": op.get("description",""),
                "parameters": list(op.get("parameters",[])),
                "responses": {str(c):{"description":r.get("description","Response")}
                              for c,r in op.get("responses",{}).items()},
                "tags": op.get("tags",[]), "produces":["application/json"],
                "consumes":["application/json"],
            }
            if "requestBody" in op:
                nop["parameters"].append({
                    "in":"body","name":"body","required":op["requestBody"].get("required",False),
                    "schema":(op["requestBody"].get("content",{})
                              .get("application/json",{}).get("schema",{}))})
            sw["paths"][path_str][m] = nop
    if spec.get("components",{}).get("schemas"):
        sw["definitions"] = spec["components"]["schemas"]
    return sw
