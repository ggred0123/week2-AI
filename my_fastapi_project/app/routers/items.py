from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.item import Item, ItemCreate
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[Item])
async def read_items():
    return []

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate):
    return {"id": 1, **item.dict()}

@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    return {"id": item_id, "name": "Test Item", "description": "This is a test item"}
