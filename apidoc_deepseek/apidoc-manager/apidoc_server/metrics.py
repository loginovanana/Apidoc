"""Prometheus metrics for APIDoc Server."""

import time
from typing import Callable

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class MetricsManager:
    def __init__(self):
        self.http_requests_total = Counter("apidoc_http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
        self.http_request_duration_seconds = Histogram("apidoc_http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"], buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10))
        self.http_requests_in_progress = Gauge("apidoc_http_requests_in_progress", "HTTP requests in progress", ["method", "endpoint"])
        self.specifications_total = Gauge("apidoc_specifications_total", "Total number of specifications")
        self.database_connections = Gauge("apidoc_database_connections", "Active database connections")
    
    def record_request(self, method: str, path: str, status_code: int, duration: float):
        self.http_requests_total.labels(method=method, endpoint=path, status=str(status_code)).inc()
        self.http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)
    
    def track_in_progress(self, method: str, path: str):
        def start(): self.http_requests_in_progress.labels(method=method, endpoint=path).inc()
        def end(): self.http_requests_in_progress.labels(method=method, endpoint=path).dec()
        return start, end


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, metrics_manager: MetricsManager):
        super().__init__(app)
        self.metrics = metrics_manager
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start, end = self.metrics.track_in_progress(request.method, request.url.path)
        start()
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            self.metrics.record_request(request.method, request.url.path, response.status_code, duration)
            return response
        except Exception:
            self.metrics.record_request(request.method, request.url.path, 500, time.time() - start_time)
            raise
        finally:
            end()


metrics = MetricsManager()


async def metrics_endpoint():
    from fastapi import Response
    return Response(content=generate_latest(), media_type="text/plain")
