"""CORS middleware configuration."""

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI, allowed_origins: List[str] = None, allowed_methods: List[str] = None, allowed_headers: List[str] = None, allow_credentials: bool = True, max_age: int = 600) -> None:
    app.add_middleware(CORSMiddleware, allow_origins=allowed_origins or ["*"], allow_credentials=allow_credentials, allow_methods=allowed_methods or ["*"], allow_headers=allowed_headers or ["*"], max_age=max_age)
