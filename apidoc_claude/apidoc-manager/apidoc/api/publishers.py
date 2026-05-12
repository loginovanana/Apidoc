"""External publishing service clients."""
from __future__ import annotations
import base64, json
from typing import Any
import httpx
from loguru import logger
from apidoc.config import settings
from apidoc.utils.errors import AuthError, NetworkError, ServerError

def _require(val, name, env): 
    if not val: raise AuthError(f"Missing {name} token", f"Set {env}")
    return val

def publish_swaggerhub(spec: dict[str, Any], api_name: str, version: str) -> dict:
    token = _require(settings.swaggerhub_token, "SwaggerHub", "APIDOC_SWAGGERHUB_TOKEN")
    owner = _require(settings.swaggerhub_owner, "SwaggerHub owner", "APIDOC_SWAGGERHUB_OWNER")
    url = f"https://api.swaggerhub.com/apis/{owner}/{api_name}/{version}"
    try:
        r = httpx.put(url, content=json.dumps(spec),
                      headers={"Authorization": token, "Content-Type": "application/json"}, timeout=30)
        if r.status_code == 401: raise AuthError("SwaggerHub: invalid token")
        if r.status_code >= 500: raise ServerError(f"SwaggerHub {r.status_code}")
        r.raise_for_status()
        return {"service": "swaggerhub", "status": "published", "url": url}
    except httpx.ConnectError as e: raise NetworkError("Cannot reach SwaggerHub") from e

def publish_github(spec_content: str, filename: str = "openapi.yaml",
                   message: str = "Update OpenAPI spec") -> dict:
    token = _require(settings.github_token, "GitHub", "APIDOC_GITHUB_TOKEN")
    repo  = _require(settings.github_repo,  "GitHub repo", "APIDOC_GITHUB_REPO")
    url   = f"https://api.github.com/repos/{repo}/contents/{filename}"
    hdrs  = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
             "X-GitHub-Api-Version": "2022-11-28"}
    try:
        get_r = httpx.get(url, headers=hdrs, timeout=15)
        sha   = get_r.json().get("sha") if get_r.status_code == 200 else None
        body: dict[str, Any] = {"message": message,
                                  "content": base64.b64encode(spec_content.encode()).decode()}
        if sha: body["sha"] = sha
        put_r = httpx.put(url, json=body, headers=hdrs, timeout=30)
        if put_r.status_code == 401: raise AuthError("GitHub: invalid token")
        put_r.raise_for_status()
        return {"service": "github", "status": "published",
                "url": put_r.json().get("content", {}).get("html_url", url)}
    except httpx.ConnectError as e: raise NetworkError("Cannot reach GitHub") from e

def publish_gitlab(spec_content: str, filename: str = "openapi.yaml",
                   branch: str = "main") -> dict:
    token = _require(settings.gitlab_token, "GitLab", "APIDOC_GITLAB_TOKEN")
    pid   = _require(settings.gitlab_project_id, "GitLab project ID", "APIDOC_GITLAB_PROJECT_ID")
    url   = f"https://gitlab.com/api/v4/projects/{pid}/repository/files/{filename.replace('/','%2F')}"
    hdrs  = {"PRIVATE-TOKEN": token, "Content-Type": "application/json"}
    body  = {"branch": branch, "content": spec_content, "commit_message": "Update OpenAPI spec"}
    try:
        r = httpx.put(url, json=body, headers=hdrs, timeout=30)
        if r.status_code == 400: r = httpx.post(url, json=body, headers=hdrs, timeout=30)
        if r.status_code == 401: raise AuthError("GitLab: invalid token")
        r.raise_for_status()
        return {"service": "gitlab", "status": "published"}
    except httpx.ConnectError as e: raise NetworkError("Cannot reach GitLab") from e

def publish_redocly(spec: dict[str, Any], api_name: str) -> dict:
    token = _require(settings.redocly_token, "Redocly", "APIDOC_REDOCLY_TOKEN")
    url = "https://app.redocly.com/api/apis"
    try:
        r = httpx.post(url, json={"name": api_name, "definition": spec},
                       headers={"Authorization": f"Bearer {token}"}, timeout=30)
        if r.status_code == 401: raise AuthError("Redocly: invalid token")
        r.raise_for_status()
        return {"service": "redocly", "status": "published"}
    except httpx.ConnectError as e: raise NetworkError("Cannot reach Redocly") from e

def publish_readme(spec_content: str) -> dict:
    """Publish to ReadMe.com using API v2 (Bearer Auth, api.readme.com)."""
    token  = _require(settings.readme_token, "ReadMe.com", "APIDOC_README_TOKEN")
    branch = settings.readme_version or "stable"
    # API v2: POST /branches/{branch}/apis  (multipart/form-data)
    url = f"https://api.readme.com/v2/branches/{branch}/apis"
    try:
        r = httpx.post(url,
                       files={"spec": ("openapi.yaml", spec_content, "application/yaml")},
                       headers={"Authorization": f"Bearer {token}"},
                       timeout=30)
        if r.status_code == 401: raise AuthError("ReadMe.com: invalid token")
        r.raise_for_status()
        # v2 returns upload.status = "pending" | "done"
        data = r.json() if r.content else {}
        return {"service": "readme", "status": "published",
                "upload_status": data.get("upload", {}).get("status", "pending")}
    except httpx.ConnectError as e: raise NetworkError("Cannot reach ReadMe.com") from e

PUBLISHERS = {
    "swaggerhub": publish_swaggerhub,
    "github":     publish_github,
    "gitlab":     publish_gitlab,
    "redocly":    publish_redocly,
    "readme":     publish_readme,
}
