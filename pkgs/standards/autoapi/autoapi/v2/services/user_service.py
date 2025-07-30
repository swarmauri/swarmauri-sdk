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
        username: str,
        is_active: bool = True,
        **custom_fields: Any,
    ) -> User:
        """
        Ensure shadow user exists, create if missing.

        This method accepts all required User model fields as explicit parameters
        and supports custom fields for extended User models via **custom_fields.
        """
        user = await self.repository.get_by_id(user_id)

        if user is None:
            # Validate required fields
            if not username:
                from ..jsonrpc_models import create_standardized_error

                http_exc, _, _ = create_standardized_error(
                    400,
                    message="Username is required for user creation",
                    rpc_code=-32602,
                )
                raise http_exc

            # Create shadow user with all provided data
            user_data = {
                "id": user_id,
                "tenant_id": tenant_id,
                "username": username,
                "is_active": is_active,
                **custom_fields,  # Support for extended User models
            }

            user = await self.repository.create(**user_data)

            # Log business event (no direct DB operations!)
            custom_info = (
                f" with custom fields: {list(custom_fields.keys())}"
                if custom_fields
                else ""
            )
            self.logger.info(
                f"Shadow user {user_id} ({username}) added to tenant {tenant_id}{custom_info}"
            )

        return user

    async def get_by_id(self, user_id: Union[str, UUID]) -> Optional[User]:
        """Get user by ID with business logic."""
        return await self.repository.get_by_id(user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.repository.get_by_username(username)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Note: This method assumes the User model has been extended with an email field.
        If using the base User model (which doesn't include email), this method will raise an error.
        """
        return await self.repository.get_by_email(email)

    async def create(self, data: Dict[str, Any]) -> User:
        """
        Create new user with business validation.

        Validates required fields based on the base User model structure.
        Extended User models with additional fields (like email) will be handled
        automatically through the **custom_fields pattern.
        """
        # Validate required fields based on base User model
        self._validate_required_fields(data, ["username", "tenant_id"])

        # Validate field lengths for base User model fields
        field_limits = {"username": 80}

        # Add validation for custom fields if they exist
        if "email" in data:
            field_limits["email"] = 120  # Common email field length

        self._validate_field_length(data, field_limits)

        # Check for duplicate username
        if await self.repository.exists_by_username(data["username"]):
            from ..jsonrpc_models import create_standardized_error

            http_exc, _, _ = create_standardized_error(
                409,
                message=f"User with username '{data['username']}' already exists",
                rpc_code=-32099,
            )
            raise http_exc

        # Check for duplicate email if provided (for extended User models)
        if "email" in data and data["email"]:
            try:
                if await self.repository.exists_by_email(data["email"]):
                    from ..jsonrpc_models import create_standardized_error

                    http_exc, _, _ = create_standardized_error(
                        409,
                        message=f"User with email '{data['email']}' already exists",
                        rpc_code=-32099,
                    )
                    raise http_exc
            except AttributeError:
                # Email field doesn't exist in User model - skip validation
                pass

        # Set defaults
        if "is_active" not in data:
            data["is_active"] = True

        return await self.repository.create(**data)

    async def update(
        self, user_id: Union[str, UUID], data: Dict[str, Any]
    ) -> Optional[User]:
        """
        Update user with business validation.

        Handles both base User model fields and extended fields gracefully.
        """
        # Validate field lengths for base User model fields and common extensions
        field_limits = {"username": 80}
        if "email" in data:
            field_limits["email"] = 120

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

        # Check for duplicate email if changing email (for extended User models)
        if "email" in data and data["email"]:
            try:
                existing = await self.repository.get_by_email(data["email"])
                if existing and str(existing.id) != str(user_id):
                    from ..jsonrpc_models import create_standardized_error

                    http_exc, _, _ = create_standardized_error(
                        409,
                        message=f"User with email '{data['email']}' already exists",
                        rpc_code=-32099,
                    )
                    raise http_exc
            except AttributeError:
                # Email field doesn't exist in User model - skip validation
                pass

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
