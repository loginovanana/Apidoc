"""FastAPI application entry point."""
from __future__ import annotations
import os, time, uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from apidoc import __version__
from server.database import create_tables, engine
from server.routers.specs import router as specs_router

import logging
from pythonjsonlogger import jsonlogger
_log_file = os.environ.get("APIDOC_SERVER_LOG", os.path.expanduser("~/.apidoc/logs/server.log"))
_fh = logging.FileHandler(_log_file, encoding="utf-8")
_fh.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
_logger = logging.getLogger("apidoc.server")
_logger.addHandler(_fh); _logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables(); _logger.info("DB ready"); yield; await engine.dispose()

app = FastAPI(title="APIDoc Manager API", version=__version__, lifespan=lifespan,
              docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    rid = str(uuid.uuid4())[:8]; start = time.perf_counter()
    response = await call_next(request)
    _logger.info("request", extra={"request_id":rid,"method":request.method,
        "path":request.url.path,"status_code":response.status_code,
        "response_time_ms":int((time.perf_counter()-start)*1000),
        "client_ip":request.client.host if request.client else "unknown"})
    response.headers["X-Request-ID"] = rid; return response

app.include_router(specs_router)

@app.get("/health", tags=["system"])
async def health(): return {"status":"ok"}

@app.get("/health/db", tags=["system"])
async def health_db():
    try:
        from sqlalchemy import text; from server.database import AsyncSessionLocal
        async with AsyncSessionLocal() as s: await s.execute(text("SELECT 1"))
        return {"status":"ok","database":"ok"}
    except Exception as exc:
        return JSONResponse(503, content={"status":"error","database":str(exc)})

@app.get("/info", tags=["system"])
async def info():
    try:
        from sqlalchemy import func, select; from server.database import AsyncSessionLocal
        from server.models import Spec
        async with AsyncSessionLocal() as s:
            count = (await s.execute(select(func.count()).select_from(Spec))).scalar_one()
    except Exception: count = 0
    return {"version":__version__,"db_url":os.environ.get("APIDOC_DB_URL","sqlite (default)"),
            "specs_count":count}

@app.get("/", include_in_schema=False)
async def root():
    """Branded landing page with ReDoc documentation viewer."""
    from fastapi.responses import HTMLResponse
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>APIDoc Manager</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: 'Segoe UI', Arial, sans-serif; background:#0d1117; }
    .header {
      display:flex; align-items:center; gap:16px;
      padding:14px 28px; background:#161b22;
      border-bottom:2px solid #ffb6c1; position:sticky; top:0; z-index:100;
    }
    .header svg { flex-shrink:0; }
    .header-title { color:#ffb6c1; font-size:1.3rem; font-weight:700; letter-spacing:.5px; }
    .header-sub   { color:#8b949e; font-size:.82rem; margin-top:2px; }
    .links { margin-left:auto; display:flex; gap:12px; }
    .links a {
      color:#cfcfcf; text-decoration:none; font-size:.85rem; padding:5px 12px;
      border:1px solid #30363d; border-radius:6px; transition:.2s;
    }
    .links a:hover { border-color:#ffb6c1; color:#ffb6c1; }
    #redoc-container { height:calc(100vh - 62px); }
  </style>
</head>
<body>
  <div class="header">
    <svg width="42" height="42" viewBox="0 0 42 42" xmlns="http://www.w3.org/2000/svg">
      <circle cx="21" cy="21" r="20" fill="#161b22" stroke="#ffb6c1" stroke-width="1.5"/>
      <text x="21" y="26" text-anchor="middle" font-family="monospace" font-size="13" font-weight="bold" fill="#ffb6c1">api</text>
      <line x1="8" y1="31" x2="34" y2="31" stroke="#6699cc" stroke-width="1.2" stroke-dasharray="3,2"/>
    </svg>
    <div>
      <div class="header-title">APIDoc Manager</div>
      <div class="header-sub">OpenAPI Specification Server</div>
    </div>
    <div class="links">
      <a href="/docs">Swagger UI</a>
      <a href="/redoc">ReDoc</a>
      <a href="/health">Health</a>
      <a href="/info">Info</a>
    </div>
  </div>
  <div id="redoc-container"></div>
  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
  <script>
    Redoc.init('/openapi.json', {
      theme: {
        colors: { primary: { main: '#ffb6c1' } },
        sidebar: { backgroundColor: '#161b22', textColor: '#cfcfcf' },
        rightPanel: { backgroundColor: '#0d1117' },
        typography: { fontFamily: 'Segoe UI, Arial, sans-serif' }
      },
      hideDownloadButton: false,
      expandResponses: '200,201',
    }, document.getElementById('redoc-container'));
  </script>
</body>
</html>"""
    return HTMLResponse(content=html)
