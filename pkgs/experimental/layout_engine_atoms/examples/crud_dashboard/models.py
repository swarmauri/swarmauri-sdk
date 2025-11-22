"""Data models for CRUD dashboard."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(BaseModel):
    """User model."""

    id: int
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    role: UserRole
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        use_enum_values = True


class CreateUserPayload(BaseModel):
    """Payload for creating a new user."""

    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.USER


class UpdateUserPayload(BaseModel):
    """Payload for updating an existing user."""

    user_id: int
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    active: Optional[bool] = None


class DeleteUserPayload(BaseModel):
    """Payload for deleting a user."""

    user_id: int


class ToggleUserPayload(BaseModel):
    """Payload for toggling user active status."""

    user_id: int


class FilterUsersPayload(BaseModel):
    """Payload for filtering users."""

    role: Optional[Union[UserRole, Literal["all", "active"]]] = None
    active: Optional[bool] = None
    search: Optional[str] = None
