"""
Service Registry - Dependency injection for AutoAPI services.

Provides service registration, creation, and dependency injection
for the AutoAPI hook system.
"""

from __future__ import annotations

from typing import Union

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..repositories import TenantRepository, UserRepository
from .tenant_service import TenantService
from .user_service import UserService


class ServiceContext(BaseModel):
    """
    Container for all services available to hooks.

    This replaces the raw database access in hook context,
    providing high-level business operations instead.
    """

    tenant: TenantService = Field(
        ..., description="Tenant service for business operations"
    )
    user: UserService = Field(..., description="User service for business operations")

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True  # Allow service instances
        validate_assignment = True  # Validate on assignment
        use_enum_values = True  # Use enum values in serialization

    def get(self, key: str, default=None):
        """Allow dict.get() style access."""
        return getattr(self, key, default)


class ServiceRegistry:
    """Registry for creating and managing services with dependency injection."""

    @staticmethod
    def create_services(db: Union[Session, AsyncSession]) -> ServiceContext:
        """
        Create all services with their dependencies.

        This is the main entry point for service creation.
        It handles the dependency injection by creating repositories
        first, then services that depend on them.

        Args:
            db: Database session (sync or async)

        Returns:
            ServiceContext containing all initialized services
        """
        # Create repositories with database session
        tenant_repo = TenantRepository(db)
        user_repo = UserRepository(db)

        # Create services with repository dependencies
        tenant_service = TenantService(tenant_repo)
        user_service = UserService(user_repo)

        return ServiceContext(tenant=tenant_service, user=user_service)

    @staticmethod
    def create_tenant_service(db: Union[Session, AsyncSession]) -> TenantService:
        """Create just the tenant service."""
        tenant_repo = TenantRepository(db)
        return TenantService(tenant_repo)

    @staticmethod
    def create_user_service(db: Union[Session, AsyncSession]) -> UserService:
        """Create just the user service."""
        user_repo = UserRepository(db)
        return UserService(user_repo)


# Convenience function for quick service creation
def create_services(db: Union[Session, AsyncSession]) -> ServiceContext:
    """
    Convenience function to create services.

    This is a shortcut to ServiceRegistry.create_services()
    """
    return ServiceRegistry.create_services(db)
