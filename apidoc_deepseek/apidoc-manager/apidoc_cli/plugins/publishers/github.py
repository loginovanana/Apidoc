"""GitHub publisher plugin."""

import base64
import httpx
import yaml
from loguru import logger

from apidoc_cli.plugins.base import BasePublisher


class GitHubPublisher(BasePublisher):
    @property
    def name(self) -> str:
        return "github"
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    async def publish(self, spec: dict, name: str, version: str, token: str = None, repo: str = None, path: str = None, branch: str = "main", message: str = None, **kwargs) -> dict:
        if not token: raise ValueError("GitHub token is required")
        if not repo: raise ValueError("GitHub repository is required (format: owner/repo)")
        
        yaml_content = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
        content_base64 = base64.b64encode(yaml_content.encode()).decode()
        file_path = path or f"docs/openapi/{name}.yaml"
        commit_message = message or f"Update OpenAPI specification {name} v{version}"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"https://api.github.com/repos/{repo}/contents/{file_path}", params={"ref": branch}, headers=headers)
            data = {"message": commit_message, "content": content_base64, "branch": branch}
            if response.status_code == 200: data["sha"] = response.json()["sha"]
            response = await client.put(f"https://api.github.com/repos/{repo}/contents/{file_path}", json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            return {"url": result["content"]["html_url"], "sha": result["content"]["sha"], "path": file_path}
    
    async def validate_credentials(self, token: str = None, **kwargs) -> bool:
        if not token: return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.github.com/user", headers={"Authorization": f"Bearer {token}"})
                return response.status_code == 200
        except Exception:
            return False
