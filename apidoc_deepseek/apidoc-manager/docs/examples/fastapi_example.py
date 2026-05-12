"""Example FastAPI application for APIDoc Manager."""

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

app = FastAPI(title="Example User API", description="A sample API for demonstrating APIDoc Manager", version="1.0.0")


class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    age: Optional[int] = Field(None, ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str


@app.get("/users", tags=["users"])
async def list_users(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    return {"items": [], "total": 0, "page": page, "limit": limit}


@app.post("/users", tags=["users"], status_code=201)
async def create_user(user: CreateUserRequest):
    return {"id": 1, "name": user.name, "email": user.email}


@app.get("/users/{user_id}", tags=["users"])
async def get_user(user_id: int):
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}


@app.put("/users/{user_id}", tags=["users"])
async def update_user(user_id: int, user: CreateUserRequest):
    return {"id": user_id, "name": user.name, "email": user.email}


@app.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int):
    return {"deleted": True}
