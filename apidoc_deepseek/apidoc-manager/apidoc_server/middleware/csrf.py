"""CSRF protection middleware."""

import hmac
import secrets
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cookie_name: str = "csrf_token", header_name: str = "X-CSRF-Token", safe_methods: set = None):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.safe_methods = safe_methods or {"GET", "HEAD", "OPTIONS"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in self.safe_methods:
            response = await call_next(request)
            return self._set_csrf_cookie(response)
        
        header_token = request.headers.get(self.header_name)
        cookie_token = request.cookies.get(self.cookie_name)
        if not header_token or not cookie_token:
            return Response(content='{"error": "CSRF token missing"}', status_code=HTTP_403_FORBIDDEN, media_type="application/json")
        if not hmac.compare_digest(header_token, cookie_token):
            return Response(content='{"error": "CSRF token mismatch"}', status_code=HTTP_403_FORBIDDEN, media_type="application/json")
        return await call_next(request)
    
    def _generate_csrf_token(self) -> str:
        return secrets.token_hex(32)
    
    def _set_csrf_cookie(self, response: Response) -> Response:
        token = self._generate_csrf_token()
        response.set_cookie(key=self.cookie_name, value=token, httponly=False, secure=True, samesite="strict", max_age=86400)
        return response
