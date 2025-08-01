"""
Generic Service and Repository - Auto-generated data access and business logic.

This module provides generic implementations that can be automatically instantiated
for any SQLAlchemy model, eliminating the need to manually create repository and
service classes for basic operations.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..repositories.base import BaseRepository
from .base import BaseService

T = TypeVar("T")


class GenericRepository(BaseRepository):
    """
    Auto-generated repository for any SQLAlchemy model.

    Provides all basic database operations without needing manual implementation.
    """

    def __init__(self, db: Union[Session, AsyncSession], model_class: Type[T]):
        super().__init__(db, model_class)


class GenericService(BaseService):
    """
    Auto-generated service for any SQLAlchemy model.

    Provides business logic layer with validation and the ensure_exists pattern
    that hooks should use instead of direct database access.
    """

    def __init__(self, repository: GenericRepository, model_class: Type[T]):
        super().__init__(repository)
        self.model_class = model_class
        self.logger = logging.getLogger(f"{__name__}.{model_class.__name__}")

        # Auto-detect required fields and constraints
        self._required_fields = self._discover_required_fields()
        self._field_limits = self._discover_field_limits()

        # Add special methods for specific models
        self._add_model_specific_methods()

    def _discover_required_fields(self) -> List[str]:
        """
        Auto-discover required fields from the model.

        Returns fields that are nullable=False (excluding primary key and timestamps).
        """
        required_fields = []

        for column_name, column in self.model_class.__table__.columns.items():
            # Skip auto-generated fields
            if (
                column.primary_key
                or column.default is not None
                or column.server_default is not None
                or column_name in ("id", "created_at", "updated_at")
            ):
                continue

            # Include fields that are nullable=False
            if not column.nullable:
                required_fields.append(column_name)

        return required_fields

    def _discover_field_limits(self) -> Dict[str, int]:
        """
        Auto-discover field length limits from the model.

        Returns dictionary of field_name: max_length for String columns.
        """
        field_limits = {}

        for column_name, column in self.model_class.__table__.columns.items():
            if hasattr(column.type, "length") and column.type.length:
                field_limits[column_name] = column.type.length

        return field_limits

    def _add_model_specific_methods(self):
        """Add special methods for specific model types."""
        model_name = self.model_class.__name__

        # Add ensure_shadow_user for User models
        if model_name == "User":
            # Dynamically add the ensure_shadow_user method
            self.ensure_shadow_user = self._create_ensure_shadow_user_method()

    def _create_ensure_shadow_user_method(self):
        """Create the ensure_shadow_user method for User models."""

        async def ensure_shadow_user(
            user_id: Union[str, UUID],
            tenant_id: Union[str, UUID],
            username: str,  # Required field
            is_active: bool = True,
            **custom_fields: Any,  # Support for extended User models
        ) -> T:
            """
            Ensure shadow user exists, create if missing.

            This method accepts all required User model fields as explicit parameters
            and supports custom fields for extended User models via **custom_fields.
            """
            # Check if user already exists
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

                # Log business event
                custom_info = (
                    f" with custom fields: {list(custom_fields.keys())}"
                    if custom_fields
                    else ""
                )
                self.logger.info(
                    f"Shadow user {user_id} ({username}) added to tenant {tenant_id}{custom_info}"
                )

            return user

        return ensure_shadow_user

    async def ensure_exists(self, id: Union[str, UUID], **required_data: Any) -> T:
        """
        Ensure entity exists, create if missing.

        This is the key method hooks should use instead of direct DB calls.
        It follows the same pattern as ensure_shadow_user but works for any model.

        Args:
            id: Primary key of the entity
            **required_data: Required fields and any custom fields

        Returns:
            The existing or newly created entity

        Example:
            # For any model, hooks can use:
            entity = await services.{model_name}.ensure_exists(
                id=entity_id,
                tenant_id=tenant_id,  # if TenantBound
                name="Entity Name",   # if required
                **custom_fields
            )
        """
        # Check if entity already exists
        entity = await self.repository.get_by_id(id)

        if entity is None:
            # Validate required fields are provided
            missing_fields = [
                field for field in self._required_fields if field not in required_data
            ]

            if missing_fields:
                from ..jsonrpc_models import create_standardized_error

                http_exc, _, _ = create_standardized_error(
                    400,
                    message=f"Missing required fields for {self.model_class.__name__}: {', '.join(missing_fields)}",
                    rpc_code=-32602,
                )
                raise http_exc

            # Create entity with all provided data
            entity_data = {
                "id": id,
                **required_data,
            }

            entity = await self.repository.create(**entity_data)

            # Log business event
            self.logger.info(
                f"{self.model_class.__name__} {id} created via ensure_exists"
            )

        return entity

    async def create(self, data: Dict[str, Any]) -> T:
        """Create new entity with auto-discovered validation."""
        # Validate required fields
        self._validate_required_fields(data, self._required_fields)

        # Validate field lengths
        self._validate_field_length(data, self._field_limits)

        return await self.repository.create(**data)

    async def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Update entity with auto-discovered validation."""
        # Validate field lengths for provided fields
        relevant_limits = {k: v for k, v in self._field_limits.items() if k in data}
        self._validate_field_length(data, relevant_limits)

        return await self.repository.update_by_id(id, **data)

    # Delegate other operations to repository
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID."""
        return await self.repository.get_by_id(id)

    async def exists(self, id: Any) -> bool:
        """Check if entity exists."""
        return await self.repository.exists(id)

    async def delete(self, id: Any) -> bool:
        """Delete entity."""
        return await self.repository.delete_by_id(id)

    async def find_by(self, **filters) -> List[T]:
        """Find entities by filters."""
        return await self.repository.find_by(**filters)

    async def find_one_by(self, **filters) -> Optional[T]:
        """Find single entity by filters."""
        return await self.repository.find_one_by(**filters)

    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """List all entities with pagination."""
        return await self.repository.list_all(limit=limit, offset=offset)

    async def count(self) -> int:
        """Count entities."""
        return await self.repository.count()


def create_generic_service(
    db: Union[Session, AsyncSession], model_class: Type[T]
) -> GenericService[T]:
    """
    Factory function to create a generic service for any model.

    Args:
        db: Database session
        model_class: SQLAlchemy model class

    Returns:
        Generic service instance for the model
    """
    repository = GenericRepository(db, model_class)
    service = GenericService(repository, model_class)
    return service
