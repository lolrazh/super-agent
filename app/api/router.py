"""Main API router module."""
from fastapi import APIRouter
from . import auth, users, system

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

# Include user routes
router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Include system routes
router.include_router(
    system.router,
    prefix="/system",
    tags=["system"]
) 