"""
AutoAPI v2 Service Layer

Provides business logic abstractions for AutoAPI operations.
Services handle business rules, validation, and orchestration,
delegating data access to repository layer.

Auto-Generation Support:
All services are now auto-generated for any registered model.
No hardcoded services needed - everything uses GenericService pattern.
"""

from .base import BaseService
from .registry import ServiceContext
from .generic import GenericService, GenericRepository, create_generic_service
from .auto_registry import AutoServiceRegistry, create_auto_services

__all__ = [
    "BaseService",
    "ServiceContext",
    # Auto-generation components (primary interface)
    "GenericService",
    "GenericRepository",
    "create_generic_service",
    "AutoServiceRegistry",
    "create_auto_services",
]
