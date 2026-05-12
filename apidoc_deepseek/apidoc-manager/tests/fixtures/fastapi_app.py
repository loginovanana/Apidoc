"""Sample FastAPI application for testing."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Test FastAPI App", version="1.0.0")


class Item(BaseModel):
    id: int
    name: str
    price: float


class CreateItemRequest(BaseModel):
    name: str
    price: float


@app.get("/items", tags=["items"])
async def list_items():
    return {"items": []}


@app.post("/items", tags=["items"])
async def create_item(item: CreateItemRequest):
    return {"id": 1, "name": item.name, "price": item.price}


@app.get("/items/{item_id}", tags=["items"])
async def get_item(item_id: int):
    return {"id": item_id, "name": "Item", "price": 10.0}


@app.delete("/items/{item_id}", tags=["items"])
async def delete_item(item_id: int):
    return {"deleted": True}
