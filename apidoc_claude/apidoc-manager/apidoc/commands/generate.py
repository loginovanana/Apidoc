"""Generate command helpers - interactive wizard."""
from __future__ import annotations
import re
from typing import Any
from rich.prompt import Confirm, Prompt
from apidoc.utils.output import console, success

HTTP_METHODS = ["GET","POST","PUT","PATCH","DELETE"]

def _interactive_wizard() -> dict[str, Any]:
    """Interactive step-by-step spec builder."""
    console.print("\n[bold cyan]╔══ APIDoc Interactive Spec Builder ══╗[/]\n")
    title   = Prompt.ask("[bold]API name[/]", default="My API")
    version = Prompt.ask("[bold]API version[/]", default="1.0.0")
    desc    = Prompt.ask("[bold]Description[/]", default="")
    srv_url = Prompt.ask("[bold]Server URL[/]", default="http://localhost:8000")
    spec: dict[str, Any] = {"openapi":"3.1.0","info":{"title":title,"version":version},
                             "servers":[{"url":srv_url}],"paths":{}}
    if desc: spec["info"]["description"] = desc
    console.print("\n[bold]── Endpoints ──[/] (leave path empty to finish)\n")
    while True:
        path_str = Prompt.ask("  Endpoint path", default="")
        if not path_str: break
        method  = Prompt.ask("  HTTP method", choices=HTTP_METHODS, default="GET")
        summary = Prompt.ask("  Summary", default="")
        has_body = method in ("POST","PUT","PATCH") and Confirm.ask("  Add request body?", default=True)
        status  = Prompt.ask("  Success code", default="200")
        rdesc   = Prompt.ask("  Success description", default="Successful Response")
        responses: dict = {status:{"description":rdesc}}
        if Confirm.ask("  Add 400 Bad Request?", default=True): responses["400"]={"description":"Bad Request"}
        op: dict = {"summary":summary,
                    "operationId":f"{method.lower()}_{path_str.strip('/').replace('/','_')}",
                    "responses":responses}
        if has_body: op["requestBody"]={"required":True,"content":{"application/json":{"schema":{"type":"object"}}}}
        params = re.findall(r"{(\w+)}", path_str)
        if params: op["parameters"]=[{"name":p,"in":"path","required":True,"schema":{"type":"string"}} for p in params]
        key = path_str if path_str.startswith("/") else f"/{path_str}"
        spec["paths"].setdefault(key,{})[method.lower()] = op
        success(f"Added {method} {key}")
    if Confirm.ask("\nAdd Bearer token security?", default=False):
        spec["components"]={"securitySchemes":{"bearerAuth":{"type":"http","scheme":"bearer","bearerFormat":"JWT"}}}
        spec["security"]=[{"bearerAuth":[]}]
    return spec
