"""ReadMe.com publisher plugin."""

import httpx
from loguru import logger

from apidoc_cli.plugins.base import BasePublisher


class ReadMePublisher(BasePublisher):
    @property
    def name(self) -> str:
        return "readme"
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    async def publish(self, spec: dict, name: str, version: str, api_key: str = None, **kwargs) -> dict:
        if not api_key: raise ValueError("ReadMe API key is required")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("https://dash.readme.com/api/v1/api-registry", json={"spec": spec, "version": version, "title": name}, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
    
    async def validate_credentials(self, api_key: str = None, **kwargs) -> bool:
        if not api_key: return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://dash.readme.com/api/v1", headers={"Authorization": f"Bearer {api_key}"})
                return response.status_code == 200
        except Exception:
            return False
