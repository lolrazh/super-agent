"""System API endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthCheck(BaseModel):
    """Health check response schema."""
    status: str
    version: str

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0"
    }

@router.get("/version")
async def version():
    """Get API version."""
    return {
        "version": "0.1.0",
        "name": "Super Agent API",
        "description": "An open-source Manus/Genspark clone for autonomous AI agents"
    } 