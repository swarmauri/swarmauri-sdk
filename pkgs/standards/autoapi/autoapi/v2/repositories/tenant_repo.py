"""
Tenant Repository - Data access for tenant entities.

Provides specialized data access methods for tenant operations.
"""

from __future__ import annotations

from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .base import BaseRepository
from ..tables.tenant import Tenant


class TenantRepository(BaseRepository):
    """Repository for tenant data access operations."""

    def __init__(self, db: Union[Session, AsyncSession]):
        super().__init__(db, Tenant)

    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name."""
        return await self.find_one_by(name=name)

    async def get_active_tenants(self) -> List[Tenant]:
        """Get all active tenants."""
        return await self.find_by(is_active=True)

    async def exists_by_name(self, name: str) -> bool:
        """Check if tenant exists by name."""
        tenant = await self.get_by_name(name)
        return tenant is not None

    async def activate_tenant(self, tenant_id: Union[str, UUID]) -> Optional[Tenant]:
        """Activate a tenant."""
        return await self.update_by_id(tenant_id, is_active=True)

    async def deactivate_tenant(self, tenant_id: Union[str, UUID]) -> Optional[Tenant]:
        """Deactivate a tenant."""
        return await self.update_by_id(tenant_id, is_active=False)
