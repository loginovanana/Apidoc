"""APIDoc Server - FastAPI application."""

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from loguru import logger

from apidoc_server.api import auth, diff, import_export, search, specs, versions
from apidoc_server.config import settings
from apidoc_server.database import engine, init_db
from apidoc_server.logging_config import setup_production_logging
from apidoc_server.metrics import MetricsMiddleware, metrics, metrics_endpoint
from apidoc_server.security import CSRFMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    setup_production_logging(log_level=settings.log_level, json_format=settings.log_json)
    logger.info("Starting APIDoc Server...")
    await init_db()
    logger.info(f"Database initialized at {settings.database_url}")
    yield
    logger.info("Shutting down APIDoc Server...")
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="APIDoc Manager API",
        description="Centralized OpenAPI specification management",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.enable_docs else None,
        redoc_url="/api/redoc" if settings.enable_docs else None,
    )
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token"],
    )
    
    if settings.enable_metrics:
        app.add_middleware(MetricsMiddleware, metrics_manager=metrics)
    
    # CSRF Protection - enabled for production
    app.add_middleware(
        CSRFMiddleware,
        cookie_name="csrf_token",
        header_name="X-CSRF-Token",
        safe_methods={"GET", "HEAD", "OPTIONS"}
    )
    
    # Root endpoint with animated logo
    logo_html_path = Path(__file__).parent / "static" / "logo.html"
    
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def root():
        """Animated logo landing page."""
        if logo_html_path.exists():
            html_content = logo_html_path.read_text(encoding="utf-8")
        else:
            # Fallback if logo.html doesn't exist
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>APIDoc Manager</title>
    <style>
        body {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
        }}
        .container {{
            text-align: center;
            color: white;
        }}
        h1 {{
            font-size: 48px;
            letter-spacing: 5px;
            text-shadow: 0 0 20px rgba(255, 182, 193, 0.5);
            margin-bottom: 10px;
        }}
        p {{
            color: #cfcfcf;
            letter-spacing: 3px;
        }}
        .links {{
            margin-top: 30px;
        }}
        .links a {{
            color: #ffb6c1;
            text-decoration: none;
            margin: 0 15px;
            padding: 10px 25px;
            border: 1px solid #ffb6c1;
            border-radius: 25px;
            transition: all 0.3s;
        }}
        .links a:hover {{
            background: rgba(255, 182, 193, 0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>APIDOC MANAGER</h1>
        <p>OpenAPI Specification Automation Toolkit</p>
        <div class="links">
            <a href="/api/docs">API Docs</a>
            <a href="/health">Health</a>
            <a href="/metrics">Metrics</a>
        </div>
    </div>
</body>
</html>"""
        return HTMLResponse(content=html_content)
    
    # API routes - search must be before specs to avoid route conflict
    app.include_router(search.router, prefix="/api/v1", tags=["Search"])
    app.include_router(specs.router, prefix="/api/v1", tags=["Specifications"])
    app.include_router(versions.router, prefix="/api/v1", tags=["Versions"])
    app.include_router(diff.router, prefix="/api/v1", tags=["Diff"])
    app.include_router(import_export.router, prefix="/api/v1", tags=["Import/Export"])
    app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
    
    if settings.enable_metrics:
        @app.get("/metrics", include_in_schema=False)
        async def get_metrics():
            return await metrics_endpoint()
    
    @app.get("/health", include_in_schema=False)
    async def health_check():
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/health/readiness", include_in_schema=False)
    async def readiness_check():
        try:
            from sqlalchemy import text
            from apidoc_server.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            return {"status": "ready"}
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return {"status": "not ready", "error": str(e)}
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apidoc_server.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )