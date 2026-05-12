"""Publish service for external services."""

import base64
from typing import Any, Dict, List

import httpx
import yaml
from loguru import logger


class PublishService:
    def __init__(self):
        self.services = {"swaggerhub": self._publish_to_swaggerhub, "github": self._publish_to_github, "readme": self._publish_to_readme, "redocly": self._publish_to_redocly}
    
    async def publish(self, spec: Dict[str, Any], targets: List[str], credentials: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for target in targets:
            if target in self.services:
                try:
                    result = await self.services[target](spec, credentials.get(target, {}), metadata.get(target, {}))
                    results[target] = {"success": True, "result": result}
                    logger.info(f"Published to {target} successfully")
                except Exception as e:
                    results[target] = {"success": False, "error": str(e)}
                    logger.error(f"Failed to publish to {target}: {e}")
        return results
    
    async def _publish_to_swaggerhub(self, spec: Dict, credentials: Dict, metadata: Dict) -> Dict:
        api_key = credentials.get("api_key")
        owner = metadata.get("owner")
        name = metadata.get("name", "api")
        version = metadata.get("version", "1.0.0")
        if not api_key or not owner: raise ValueError("SwaggerHub requires api_key and owner")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"https://api.swaggerhub.com/apis/{owner}/{name}"
            response = await client.post(url, params={"version": version}, json=spec, headers={"Authorization": api_key, "Content-Type": "application/json"})
            if response.status_code == 409:
                response = await client.put(f"{url}/{version}", json=spec, headers={"Authorization": api_key, "Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
    
    async def _publish_to_github(self, spec: Dict, credentials: Dict, metadata: Dict) -> Dict:
        token = credentials.get("token")
        repo = metadata.get("repo")
        path = metadata.get("path", "openapi.yaml")
        branch = metadata.get("branch", "main")
        if not token or not repo: raise ValueError("GitHub requires token and repo")
        
        yaml_content = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
        content_base64 = base64.b64encode(yaml_content.encode()).decode()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"https://api.github.com/repos/{repo}/contents/{path}", params={"ref": branch}, headers=headers)
            data = {"message": "Update OpenAPI specification", "content": content_base64, "branch": branch}
            if response.status_code == 200: data["sha"] = response.json()["sha"]
            response = await client.put(f"https://api.github.com/repos/{repo}/contents/{path}", json=data, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def _publish_to_readme(self, spec: Dict, credentials: Dict, metadata: Dict) -> Dict:
        api_key = credentials.get("api_key")
        version = metadata.get("version", "1.0.0")
        if not api_key: raise ValueError("ReadMe requires api_key")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("https://dash.readme.com/api/v1/api-registry", json={"spec": spec, "version": version}, headers={"Authorization": f"Bearer {api_key}"})
            response.raise_for_status()
            return response.json()
    
    async def _publish_to_redocly(self, spec: Dict, credentials: Dict, metadata: Dict) -> Dict:
        api_key = credentials.get("api_key")
        organization = metadata.get("organization")
        name = metadata.get("name", "api")
        version = metadata.get("version", "1.0.0")
        if not api_key or not organization: raise ValueError("Redocly requires api_key and organization")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"https://api.redocly.com/orgs/{organization}/apis", json={"name": name, "version": version, "spec": spec}, headers={"Authorization": f"Bearer {api_key}"})
            if response.status_code == 409:
                apis_response = await client.get(f"https://api.redocly.com/orgs/{organization}/apis", headers={"Authorization": f"Bearer {api_key}"})
                api_id = None
                for api in apis_response.json().get("items", []):
                    if api.get("name") == name: api_id = api.get("id"); break
                if api_id:
                    response = await client.put(f"https://api.redocly.com/orgs/{organization}/apis/{api_id}/versions/{version}", json={"spec": spec}, headers={"Authorization": f"Bearer {api_key}"})
            response.raise_for_status()
            return response.json()
