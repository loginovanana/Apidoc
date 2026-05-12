"""Rate limiting middleware."""

import time
from collections import defaultdict
from typing import Callable, Dict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000, whitelist: list = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.whitelist = whitelist or ["127.0.0.1", "localhost"]
        self._storage: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        if client_ip in self.whitelist:
            return await call_next(request)
        
        if not self._check_rate_limit(client_ip):
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": "60", "X-RateLimit-Limit": str(self.requests_per_minute)}
            )
        
        response = await call_next(request)
        remaining = self._get_remaining_requests(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded: return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip: return real_ip
        if request.client: return request.client.host
        return "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        now = time.time()
        self._clean_old_entries(client_ip, now)
        requests = self._storage.get(client_ip, [])
        if len([r for r in requests if now - r < 60]) >= self.requests_per_minute: return False
        if len([r for r in requests if now - r < 3600]) >= self.requests_per_hour: return False
        requests.append(now)
        self._storage[client_ip] = requests
        return True
    
    def _clean_old_entries(self, client_ip: str, now: float) -> None:
        if client_ip in self._storage:
            self._storage[client_ip] = [r for r in self._storage[client_ip] if now - r < 3600]
    
    def _get_remaining_requests(self, client_ip: str) -> int:
        now = time.time()
        requests = self._storage.get(client_ip, [])
        return max(0, self.requests_per_minute - len([r for r in requests if now - r < 60]))
