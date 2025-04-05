"""User model module."""
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """User model for authentication and authorization."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False) 