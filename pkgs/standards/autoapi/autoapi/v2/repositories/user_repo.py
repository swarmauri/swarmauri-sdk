"""
User Repository - Data access for user entities.

Provides specialized data access methods for user operations.
"""

from __future__ import annotations

from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .base import BaseRepository
from ..tables.user import User


class UserRepository(BaseRepository):
    """Repository for user data access operations."""

    def __init__(self, db: Union[Session, AsyncSession]):
        super().__init__(db, User)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.find_one_by(username=username)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.find_one_by(email=email)

    async def get_users_by_tenant(self, tenant_id: Union[str, UUID]) -> List[User]:
        """Get all users for a specific tenant."""
        return await self.find_by(tenant_id=tenant_id)

    async def get_active_users_by_tenant(
        self, tenant_id: Union[str, UUID]
    ) -> List[User]:
        """Get active users for a specific tenant."""
        return await self.find_by(tenant_id=tenant_id, is_active=True)

    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        user = await self.get_by_username(username)
        return user is not None

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        user = await self.get_by_email(email)
        return user is not None

    async def activate_user(self, user_id: Union[str, UUID]) -> Optional[User]:
        """Activate a user."""
        return await self.update_by_id(user_id, is_active=True)

    async def deactivate_user(self, user_id: Union[str, UUID]) -> Optional[User]:
        """Deactivate a user."""
        return await self.update_by_id(user_id, is_active=False)

    async def update_username(
        self, user_id: Union[str, UUID], username: str
    ) -> Optional[User]:
        """Update user's username."""
        return await self.update_by_id(user_id, username=username)

    async def update_email(
        self, user_id: Union[str, UUID], email: str
    ) -> Optional[User]:
        """Update user's email."""
        return await self.update_by_id(user_id, email=email)
