"""Main API router module."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Super Agent API"} 