"""Security utilities."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from apidoc_server.config import settings


class SecurityManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.algorithm = "HS256"
        self.secret_key = settings.secret_key
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.token_expire_minutes))
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            return payload
        except JWTError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")
    
    def generate_api_key(self) -> Tuple[str, str]:
        api_key = f"ak_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return api_key, key_hash


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        safe_methods: set = None,
        exemption_paths: set = None,
    ):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.safe_methods = safe_methods or {"GET", "HEAD", "OPTIONS"}
        self.exemption_paths = exemption_paths or {
            "/api/v1/auth/token",
            "/api/v1/auth/refresh",
            "/health",
            "/health/readiness",
            "/metrics",
            "/api/docs",
            "/api/redoc",
            "/",  # Landing page
            "/favicon.ico",
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Allow exempted paths without CSRF check
        if request.url.path in self.exemption_paths:
            response = await call_next(request)
            return self._set_csrf_cookie(response)
        
        if request.method in self.safe_methods:
            response = await call_next(request)
            return self._set_csrf_cookie(response)
        
        header_token = request.headers.get(self.header_name)
        cookie_token = request.cookies.get(self.cookie_name)
        
        if not header_token or not cookie_token:
            return Response(
                content='{"error": "CSRF token missing"}',
                status_code=status.HTTP_403_FORBIDDEN,
                media_type="application/json"
            )
        if not hmac.compare_digest(header_token, cookie_token):
            return Response(
                content='{"error": "CSRF token mismatch"}',
                status_code=status.HTTP_403_FORBIDDEN,
                media_type="application/json"
            )
        
        return await call_next(request)
    
    def _generate_csrf_token(self) -> str:
        """Generate a random CSRF token."""
        return secrets.token_hex(32)
    
    def _set_csrf_cookie(self, response: Response) -> Response:
        """Set CSRF token cookie on safe responses."""
        token = self._generate_csrf_token()
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            httponly=False,  # Must be readable by JavaScript
            secure=True,
            samesite="strict",
            max_age=86400  # 24 hours
        )
        return response


security_manager = SecurityManager()
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    payload = security_manager.verify_token(token)
    return {"username": payload.get("sub"), "scopes": payload.get("scopes", [])}