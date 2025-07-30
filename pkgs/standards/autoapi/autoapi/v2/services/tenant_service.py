"""
Tenant Service - Business logic for tenant operations.

Handles tenant-related business rules, validation, and operations.
Abstracts database operations from hook consumers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import HTTPException, status

from .base import BaseService
from ..repositories.tenant_repo import TenantRepository
from ..tables.tenant import Tenant


class TenantService(BaseService):
    """Service for tenant business operations."""

    def __init__(self, repository: TenantRepository):
        super().__init__(repository)
        self.repository = repository  # Type hint for IDE

    async def ensure_exists(self, tenant_id: Union[str, UUID]) -> None:
        """
        Ensure tenant exists, raise 403 if not.

        This is the key method that replaces direct database access
        in hooks for tenant validation.
        """
        if not await self.repository.exists(tenant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tenant {tenant_id} is not registered in Peagen.",
            )

    async def get_by_id(self, tenant_id: Union[str, UUID]) -> Optional[Tenant]:
        """Get tenant by ID with business logic."""
        return await self.repository.get_by_id(tenant_id)

    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name."""
        return await self.repository.get_by_name(name)

    async def create(self, data: Dict[str, Any]) -> Tenant:
        """Create new tenant with business validation."""
        # Validate required fields
        self._validate_required_fields(data, ["name"])

        # Validate field lengths
        self._validate_field_length(data, {"name": 100})

        # Check for duplicate name
        if await self.repository.exists_by_name(data["name"]):
            from ..jsonrpc_models import create_standardized_error

            http_exc, _, _ = create_standardized_error(
                409,
                message=f"Tenant with name '{data['name']}' already exists",
                rpc_code=-32099,
            )
            raise http_exc

        # Set defaults
        if "is_active" not in data:
            data["is_active"] = True

        return await self.repository.create(**data)

    async def update(
        self, tenant_id: Union[str, UUID], data: Dict[str, Any]
    ) -> Optional[Tenant]:
        """Update tenant with business validation."""
        # Validate field lengths if provided
        field_limits = {"name": 100}
        self._validate_field_length(
            data, {k: v for k, v in field_limits.items() if k in data}
        )

        # Check for duplicate name if changing name
        if "name" in data:
            existing = await self.repository.get_by_name(data["name"])
            if existing and str(existing.id) != str(tenant_id):
                from ..jsonrpc_models import create_standardized_error

                http_exc, _, _ = create_standardized_error(
                    409,
                    message=f"Tenant with name '{data['name']}' already exists",
                    rpc_code=-32099,
                )
                raise http_exc

        return await self.repository.update_by_id(tenant_id, **data)

    async def delete(self, tenant_id: Union[str, UUID]) -> bool:
        """Delete tenant with business rules."""
        # Business rule: Check if tenant has active users
        # This would typically query the user repository
        # For now, we'll just delete directly
        return await self.repository.delete_by_id(tenant_id)

    async def get_active_tenants(self) -> List[Tenant]:
        """Get all active tenants."""
        return await self.repository.get_active_tenants()

    async def activate(self, tenant_id: Union[str, UUID]) -> Optional[Tenant]:
        """Activate a tenant."""
        tenant = await self.repository.activate_tenant(tenant_id)
        if not tenant:
            from ..jsonrpc_models import create_standardized_error

            http_exc, _, _ = create_standardized_error(404, rpc_code=-32094)
            raise http_exc
        return tenant

    async def deactivate(self, tenant_id: Union[str, UUID]) -> Optional[Tenant]:
        """Deactivate a tenant."""
        tenant = await self.repository.deactivate_tenant(tenant_id)
        if not tenant:
            from ..jsonrpc_models import create_standardized_error

            http_exc, _, _ = create_standardized_error(404, rpc_code=-32094)
            raise http_exc
        return tenant
