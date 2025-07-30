"""
User Service - Business logic for user operations.

Handles user-related business rules, validation, and operations.
Includes the critical ensure_shadow_user functionality that replaces
direct database operations in hooks.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from .base import BaseService
from ..repositories.user_repo import UserRepository
from ..tables.user import User


class UserService(BaseService):
    """Service for user business operations."""

    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repository = repository  # Type hint for IDE
        self.logger = logging.getLogger(__name__)

    async def ensure_shadow_user(
        self,
        user_id: Union[str, UUID],
        tenant_id: Union[str, UUID],
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> User:
        """
        Ensure shadow user exists, create if missing.

        This is the key method that replaces the direct database operations
        in the bad hook example. It handles the business logic of creating
        shadow users without exposing database operations to hook consumers.
        """
        user = await self.repository.get_by_id(user_id)

        if user is None:
            # Create shadow user with business logic
            user_data = {
                "id": user_id,
                "tenant_id": tenant_id,
                "username": username or "unknown",
                "is_active": True,
            }

            # Add email if provided
            if email:
                user_data["email"] = email

            user = await self.repository.create(**user_data)

            # Log business event (no direct DB operations!)
            self.logger.info(f"Shadow user {user_id} added to tenant {tenant_id}")

        return user

    async def get_by_id(self, user_id: Union[str, UUID]) -> Optional[User]:
        """Get user by ID with business logic."""
        return await self.repository.get_by_id(user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.repository.get_by_username(username)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.repository.get_by_email(email)

    async def create(self, data: Dict[str, Any]) -> User:
        """Create new user with business validation."""
        # Validate required fields
        self._validate_required_fields(data, ["username", "tenant_id"])

        # Validate field lengths
        self._validate_field_length(data, {"username": 80, "email": 120})

        # Check for duplicate username
        if await self.repository.exists_by_username(data["username"]):
            from ..jsonrpc_models import create_standardized_error

            http_exc, _, _ = create_standardized_error(
                409,
                message=f"User with username '{data['username']}' already exists",
                rpc_code=-32099,
            )
            raise http_exc

        # Check for duplicate email if provided
        if "email" in data and data["email"]:
            if await self.repository.exists_by_email(data["email"]):
                from ..jsonrpc_models import create_standardized_error

                http_exc, _, _ = create_standardized_error(
                    409,
                    message=f"User with email '{data['email']}' already exists",
                    rpc_code=-32099,
                )
                raise http_exc

        # Set defaults
        if "is_active" not in data:
            data["is_active"] = True

        return await self.repository.create(**data)

    async def update(
        self, user_id: Union[str, UUID], data: Dict[str, Any]
    ) -> Optional[User]:
        """Update user with business validation."""
        # Validate field lengths if provided
        field_limits = {"username": 80, "email": 120}
        self._validate_field_length(
            data, {k: v for k, v in field_limits.items() if k in data}
        )

        # Check for duplicate username if changing username
        if "username" in data:
            existing = await self.repository.get_by_username(data["username"])
            if existing and str(existing.id) != str(user_id):
                from ..jsonrpc_models import create_standardized_error

                http_exc, _, _ = create_standardized_error(
                    409,
                    message=f"User with username '{data['username']}' already exists",
                    rpc_code=-32099,
                )
                raise http_exc

        # Check for duplicate email if changing email
        if "email" in data and data["email"]:
            existing = await self.repository.get_by_email(data["email"])
            if existing and str(existing.id) != str(user_id):
                from ..jsonrpc_models import create_standardized_error

                http_exc, _, _ = create_standardized_error(
                    409,
                    message=f"User with email '{data['email']}' already exists",
                    rpc_code=-32099,
                )
                raise http_exc

        return await self.repository.update_by_id(user_id, **data)

    async def delete(self, user_id: Union[str, UUID]) -> bool:
        """Delete user with business rules."""
        return await self.repository.delete_by_id(user_id)

    async def get_users_by_tenant(self, tenant_id: Union[str, UUID]) -> List[User]:
        """Get all users for a specific tenant."""
        return await self.repository.get_users_by_tenant(tenant_id)

    async def get_active_users_by_tenant(
        self, tenant_id: Union[str, UUID]
    ) -> List[User]:
        """Get active users for a specific tenant."""
        return await self.repository.get_active_users_by_tenant(tenant_id)

    async def activate(self, user_id: Union[str, UUID]) -> Optional[User]:
        """Activate a user."""
        user = await self.repository.activate_user(user_id)
        if not user:
            from ..jsonrpc_models import create_standardized_error

            http_exc, _, _ = create_standardized_error(404, rpc_code=-32094)
            raise http_exc
        return user

    async def deactivate(self, user_id: Union[str, UUID]) -> Optional[User]:
        """Deactivate a user."""
        user = await self.repository.deactivate_user(user_id)
        if not user:
            from ..jsonrpc_models import create_standardized_error

            http_exc, _, _ = create_standardized_error(404, rpc_code=-32094)
            raise http_exc
        return user
