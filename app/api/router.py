"""Main API router module."""
from fastapi import APIRouter
from . import auth

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Super Agent API"}

# Include authentication routes
router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
) 