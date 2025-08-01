"""
Service Registry Base - Foundation for AutoAPI service context.

This module provides the base ServiceContext that the auto-generation
system extends dynamically for each registered model.
"""

from __future__ import annotations

from pydantic import BaseModel


class ServiceContext(BaseModel):
    """
    Base container for all services available to hooks.

        This replaces raw database access in hook context,
    providing high-level business operations instead.

    This base class is dynamically extended by AutoServiceRegistry
    to include services for all registered models.
    """

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True  # Allow service instances
        validate_assignment = True  # Validate on assignment
        use_enum_values = True  # Use enum values in serialization

    def get(self, key: str, default=None):
        """Allow dict.get() style access."""
        return getattr(self, key, default)

    def __getitem__(self, key: str):
        """Allow dict[key] style access."""
        return getattr(self, key)
