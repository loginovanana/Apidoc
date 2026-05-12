"""SwaggerHub publisher plugin."""

import httpx
from loguru import logger

from apidoc_cli.plugins.base import BasePublisher


class SwaggerHubPublisher(BasePublisher):
    @property
    def name(self) -> str:
        return "swaggerhub"
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    async def publish(self, spec: dict, name: str, version: str, api_key: str = None, owner: str = None, is_private: bool = False, **kwargs) -> dict:
        if not api_key:
            raise ValueError("SwaggerHub API key is required")
        if not owner:
            raise ValueError("SwaggerHub owner is required")
        
        url = f"https://api.swaggerhub.com/apis/{owner}/{name}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, params={"version": version, "isPrivate": str(is_private).lower()}, json=spec, headers={"Authorization": api_key, "Content-Type": "application/json"})
            if response.status_code == 409:
                logger.info(f"API {name} already exists, updating...")
                response = await client.put(f"{url}/{version}", json=spec, headers={"Authorization": api_key, "Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
    
    async def validate_credentials(self, api_key: str = None, **kwargs) -> bool:
        if not api_key: return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.swaggerhub.com/apis", headers={"Authorization": api_key})
                return response.status_code == 200
        except Exception:
            return False
