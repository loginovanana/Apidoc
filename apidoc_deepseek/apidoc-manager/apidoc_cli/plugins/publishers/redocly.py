"""Redocly publisher plugin."""

import httpx
from loguru import logger

from apidoc_cli.plugins.base import BasePublisher


class RedoclyPublisher(BasePublisher):
    @property
    def name(self) -> str:
        return "redocly"
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    async def publish(self, spec: dict, name: str, version: str, api_key: str = None, organization: str = None, **kwargs) -> dict:
        if not api_key: raise ValueError("Redocly API key is required")
        if not organization: raise ValueError("Redocly organization is required")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"https://api.redocly.com/orgs/{organization}/apis", json={"name": name, "version": version, "spec": spec}, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
            if response.status_code == 409:
                apis_response = await client.get(f"https://api.redocly.com/orgs/{organization}/apis", headers={"Authorization": f"Bearer {api_key}"})
                api_id = None
                for api in apis_response.json().get("items", []):
                    if api.get("name") == name: api_id = api.get("id"); break
                if api_id:
                    response = await client.put(f"https://api.redocly.com/orgs/{organization}/apis/{api_id}/versions/{version}", json={"spec": spec}, headers={"Authorization": f"Bearer {api_key}"})
            response.raise_for_status()
            return response.json()
    
    async def validate_credentials(self, api_key: str = None, **kwargs) -> bool:
        if not api_key: return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.redocly.com/auth/status", headers={"Authorization": f"Bearer {api_key}"})
                return response.status_code == 200
        except Exception:
            return False
