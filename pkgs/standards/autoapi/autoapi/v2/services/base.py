"""
Base Service - Common business logic patterns for AutoAPI.

Provides base functionality for service implementations including
error handling, validation, and common business operations.
"""

from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Optional, Type, TypeVar

from ..repositories.base import BaseRepository

T = TypeVar("T")


class BaseService(ABC):
    """Base service providing common business logic patterns."""

    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID with business logic."""
        return await self.repository.get_by_id(id)

    async def exists(self, id: Any) -> bool:
        """Check if entity exists."""
        return await self.repository.exists(id)

    async def create(self, data: Dict[str, Any]) -> T:
        """Create entity with business validation."""
        # Override in subclasses to add validation
        return await self.repository.create(**data)

    async def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Update entity with business validation."""
        # Override in subclasses to add validation
        return await self.repository.update_by_id(id, **data)

    async def delete(self, id: Any) -> bool:
        """Delete entity with business rules."""
        # Override in subclasses to add business logic
        return await self.repository.delete_by_id(id)

    def _validate_required_fields(
        self, data: Dict[str, Any], required_fields: list[str]
    ) -> None:
        """Validate that required fields are present."""
        missing_fields = [
            field
            for field in required_fields
            if field not in data or data[field] is None
        ]
        if missing_fields:
            from ..jsonrpc_models import create_standardized_error

            http_exc, _, _ = create_standardized_error(
                400,
                message=f"Missing required fields: {', '.join(missing_fields)}",
                rpc_code=-32602,
            )
            raise http_exc

    def _validate_field_length(
        self, data: Dict[str, Any], field_limits: Dict[str, int]
    ) -> None:
        """Validate field length constraints."""
        for field, max_length in field_limits.items():
            if field in data and data[field] and len(str(data[field])) > max_length:
                from ..jsonrpc_models import create_standardized_error

                http_exc, _, _ = create_standardized_error(
                    400,
                    message=f"Field '{field}' exceeds maximum length of {max_length}",
                    rpc_code=-32602,
                )
                raise http_exc
