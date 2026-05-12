"""Authentication API endpoints."""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from apidoc_server.config import settings
from apidoc_server.security import security_manager

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


@router.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    
    access_token = security_manager.create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=settings.token_expire_minutes))
    refresh_token = security_manager.create_refresh_token(data={"sub": form_data.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = security_manager.verify_token(refresh_token, token_type="refresh")
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        access_token = security_manager.create_access_token(data={"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.post("/auth/api-key")
async def create_api_key(name: str, expires_in_days: Optional[int] = 30):
    api_key, key_hash = security_manager.generate_api_key()
    return {"api_key": api_key, "name": name, "expires_in_days": expires_in_days}
