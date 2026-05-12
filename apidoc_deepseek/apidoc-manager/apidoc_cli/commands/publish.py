"""Publish command."""

import asyncio
import base64
import os
from pathlib import Path
from typing import Dict, List, Optional

import httpx
import typer
import yaml
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from apidoc_cli.config import Config
from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


class Publisher:
    """Publish specifications to various services."""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def publish_to_server(self, spec: Dict, name: str, server_url: str, token: Optional[str] = None) -> Dict:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{server_url}/api/v1/specs",
                json={"name": name, "content": spec, "format": "json", "changelog": "Published via CLI"},
                headers=headers
            )
            if response.status_code == 409:
                spec_id = await self._get_spec_id(client, server_url, name, headers)
                if spec_id:
                    response = await client.post(
                        f"{server_url}/api/v1/specs/{spec_id}/versions",
                        json={"content": spec, "version": spec.get("info", {}).get("version", "1.0.0"), "format": "json", "changelog": "Updated via CLI"},
                        headers=headers
                    )
            response.raise_for_status()
            return response.json()
    
    async def _get_spec_id(self, client, server_url: str, name: str, headers: Dict) -> Optional[int]:
        response = await client.get(f"{server_url}/api/v1/specs/search", params={"q": name}, headers=headers)
        data = response.json()
        for item in data.get("items", []):
            if item["name"] == name:
                return item["id"]
        return None
    
    async def publish_to_swaggerhub(self, spec: Dict, api_key: str, owner: str, name: str, version: str) -> Dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://api.swaggerhub.com/apis/{owner}/{name}",
                params={"version": version, "isPrivate": "false"},
                json=spec,
                headers={"Authorization": api_key, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    
    async def publish_to_github(self, spec: Dict, token: str, repo: str, path: str, branch: str = "main", message: str = "Update OpenAPI specification") -> Dict:
        yaml_content = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
        content_base64 = base64.b64encode(yaml_content.encode()).decode()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                params={"ref": branch},
                headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            )
            data = {"message": message, "content": content_base64, "branch": branch}
            if response.status_code == 200:
                data["sha"] = response.json()["sha"]
            
            response = await client.put(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                json=data,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
            )
            response.raise_for_status()
            result = response.json()
            return {"url": result["content"]["html_url"], "sha": result["content"]["sha"], "path": path}
    
    async def publish_to_readme(self, spec: Dict, api_key: str, version: str) -> Dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://dash.readme.com/api/v1/api-registry",
                json={"spec": spec, "version": version},
                headers={"Authorization": f"Bearer {api_key}"}
            )
            response.raise_for_status()
            return response.json()


@app.callback()
def publish_command(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    targets: List[str] = typer.Option(["server"], "--target", "-t", help="Publish targets (server, swaggerhub, github, readme)"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="API name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="API version"),
    server_url: Optional[str] = typer.Option(None, "--server-url", help="Server URL"),
    swaggerhub_owner: Optional[str] = typer.Option(None, "--swaggerhub-owner", help="SwaggerHub owner"),
    github_repo: Optional[str] = typer.Option(None, "--github-repo", help="GitHub repository"),
    github_path: Optional[str] = typer.Option(None, "--github-path", help="Path in GitHub repo"),
) -> None:
    """Publish OpenAPI specification to various services."""
    
    cfg: Config = ctx.obj["config"]
    
    try:
        spec = read_input(spec_file)
        api_name = name or spec.get("info", {}).get("title", spec_file.stem)
        api_version = version or spec.get("info", {}).get("version", "1.0.0")
        
        console.print(f"[bold]Publishing:[/] {api_name} v{api_version}")
        
        publisher = Publisher(cfg)
        results = []
        
        # Получаем токены: сначала из конфига, потом из переменных окружения
        github_token = cfg.settings.external.github_token or os.environ.get("GITHUB_TOKEN")
        swaggerhub_key = cfg.settings.external.swaggerhub_api_key or os.environ.get("SWAGGERHUB_API_KEY")
        readme_key = cfg.settings.external.readme_api_key or os.environ.get("README_API_KEY")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            async def publish_all():
                tasks = []
                
                if "server" in targets:
                    async def pub_server():
                        url = server_url or cfg.settings.server.url
                        return await publisher.publish_to_server(spec, api_name, url, cfg.settings.server.token)
                    tasks.append(("Server", pub_server()))
                
                if "swaggerhub" in targets and swaggerhub_key:
                    async def pub_swagger():
                        return await publisher.publish_to_swaggerhub(spec, swaggerhub_key, swaggerhub_owner, api_name, api_version)
                    tasks.append(("SwaggerHub", pub_swagger()))
                
                if "github" in targets and github_token:
                    async def pub_github():
                        repo = github_repo
                        path = github_path or f"docs/openapi.yaml"
                        return await publisher.publish_to_github(spec, github_token, repo, path)
                    tasks.append(("GitHub", pub_github()))
                
                if "readme" in targets and readme_key:
                    async def pub_readme():
                        return await publisher.publish_to_readme(spec, readme_key, api_version)
                    tasks.append(("ReadMe", pub_readme()))
                
                for target_name, coro in tasks:
                    task = progress.add_task(f"Publishing to {target_name}...", total=None)
                    try:
                        result = await coro
                        results.append({"target": target_name, "success": True, "result": result})
                        progress.update(task, description=f"[green]OK Published to {target_name}[/]")
                    except Exception as e:
                        results.append({"target": target_name, "success": False, "error": str(e)})
                        progress.update(task, description=f"[red]FAIL Failed {target_name}: {e}[/]")
            
            asyncio.run(publish_all())
        
        if results:
            table = Table(title="Publish Results")
            table.add_column("Target", style="cyan")
            table.add_column("Status")
            table.add_column("Details")
            for result in results:
                if result["success"]:
                    table.add_row(result["target"], "[green]OK Success[/]", str(result.get("result", {}).get("id", "")))
                else:
                    table.add_row(result["target"], "[red]FAIL Failed[/]", result["error"])
            console.print(table)
        else:
            console.print("[yellow]No targets to publish. Check your API keys/tokens.[/]")
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if ctx.obj.get("debug"):
            console.print_exception()
        raise typer.Exit(1)