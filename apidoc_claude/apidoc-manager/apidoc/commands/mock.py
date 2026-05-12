"""Mock server builder."""
from __future__ import annotations
import json, random, string, time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def _generate_value(schema: dict, field_name: str = "") -> Any:
    if not isinstance(schema,dict): return None
    if "example" in schema: return schema["example"]
    if "enum" in schema: return schema["enum"][0]
    if "default" in schema: return schema["default"]
    typ = schema.get("type","string"); fmt = schema.get("format","")
    if typ == "integer": return random.randint(1,9999) if "id" in field_name.lower() else random.randint(0,100)
    if typ == "number": return round(random.uniform(0,1000),2)
    if typ == "boolean": return True
    if typ == "array": return [_generate_value(schema.get("items",{"type":"string"}))]
    if typ == "object":
        return {k:_generate_value(v,k) for k,v in schema.get("properties",{}).items()}
    if fmt=="date-time": return datetime.utcnow().isoformat()+"Z"
    if fmt=="date": return datetime.utcnow().date().isoformat()
    if fmt=="email": return "user@example.com"
    if fmt=="uuid": import uuid; return str(uuid.uuid4())
    if "name" in field_name.lower(): return "John Doe"
    return "".join(random.choices(string.ascii_lowercase,k=8))

def _build_response_body(operation: dict) -> Any:
    for code in ("200","201","202"):
        resp = operation.get("responses",{}).get(code,{})
        schema = resp.get("content",{}).get("application/json",{}).get("schema",{})
        if schema: return _generate_value(schema)
        if resp.get("example"): return resp["example"]
    return {"message":"OK"}

def _first_success_code(op: dict) -> int:
    for c in ("200","201","202","204"):
        if c in op.get("responses",{}): return int(c)
    return 200

def build_mock_app(spec: dict, log_file: Optional[Path], delay_ms: int) -> FastAPI:
    mock = FastAPI(title=f"[MOCK] {spec.get('info',{}).get('title','API')}",
                   version=spec.get("info",{}).get("version","1.0.0"))
    log_fh = open(log_file,"a",encoding="utf-8") if log_file else None
    for path_str, path_item in spec.get("paths",{}).items():
        for method, operation in path_item.items():
            if method.upper() not in ("GET","POST","PUT","PATCH","DELETE"): continue
            _op = dict(operation) if isinstance(operation,dict) else {}
            _code = _first_success_code(_op)
            async def _handler(request: Request, _o=_op, _s=_code) -> JSONResponse:
                start = time.perf_counter()
                if delay_ms:
                    import asyncio; await asyncio.sleep(delay_ms/1000)
                body = _build_response_body(_o)
                if log_fh:
                    log_fh.write(json.dumps({"timestamp":datetime.utcnow().isoformat()+"Z",
                        "method":request.method,"path":str(request.url.path),
                        "status_code":_s,"response_time_ms":int((time.perf_counter()-start)*1000)})+"\n")
                    log_fh.flush()
                return JSONResponse(content=body, status_code=_s)
            mock.add_api_route(path_str, _handler, methods=[method.upper()])
    return mock
