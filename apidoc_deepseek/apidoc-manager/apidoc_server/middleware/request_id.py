"""Request ID middleware."""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str = "X-Request-ID", response_header: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name
        self.response_header = response_header
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[self.response_header] = request_id
        return response
    
    @staticmethod
    def get_request_id(request: Request) -> str:
        return getattr(request.state, "request_id", str(uuid.uuid4()))
