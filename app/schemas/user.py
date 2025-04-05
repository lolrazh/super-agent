"""User schemas module."""
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation schema."""
    password: str

class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        """Pydantic config."""
        from_attributes = True 