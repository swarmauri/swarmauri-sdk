"""
Auto Service Registry - Automatically generates services for all registered models.

This module scans AutoAPI's registered models and auto-generates repository and service
layers, making them available in hooks without manual implementation.
"""

from __future__ import annotations

from typing import Dict, Set, Type, Union

from pydantic import BaseModel, create_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .generic import create_generic_service
from .registry import ServiceContext


class AutoServiceRegistry:
    """
    Registry that automatically creates services for all registered models.

    Scans the models provided to AutoAPI and creates generic services for each,
    making them available to hooks via ctx["services"].{model_name}.
    """

    @staticmethod
    def create_services(
        db: Union[Session, AsyncSession], models: Set[Type]
    ) -> BaseModel:
        """
        Create services for all registered models automatically.

        Args:
            db: Database session
            models: Set of SQLAlchemy model classes from AutoAPI(include=...)

        Returns:
            Dynamic service context with services for all models
        """
        service_dict = {}

        # Auto-generate services for ALL models (no exceptions)
        for model_class in models:
            model_name = model_class.__name__.lower()

            # Create generic service for this model
            generic_service = create_generic_service(db, model_class)
            service_dict[model_name] = generic_service

        # Create dynamic service context class
        DynamicServiceContext = create_model(
            "DynamicServiceContext",
            __base__=ServiceContext,
            **{
                name: (type(service), service) for name, service in service_dict.items()
            },
        )

        # Instantiate with all services
        return DynamicServiceContext(**service_dict)

    @staticmethod
    def get_available_services(models: Set[Type]) -> Dict[str, str]:
        """
        Get a mapping of available service names to their descriptions.

        Useful for debugging and documentation.

        Args:
            models: Set of registered model classes

        Returns:
            Dictionary of service_name: description
        """
        services = {}

        for model_class in models:
            model_name = model_class.__name__.lower()
            services[model_name] = (
                f"Auto-generated service for {model_class.__name__} model"
            )

        return services


def create_auto_services(
    db: Union[Session, AsyncSession], models: Set[Type]
) -> BaseModel:
    """
    Convenience function to create auto-generated services.

    This is the main entry point that should replace ServiceRegistry.create_services
    in the AutoAPI runner when auto-generation is enabled.

    Args:
        db: Database session
        models: Set of SQLAlchemy model classes

    Returns:
        Service context with all auto-generated services

    Example:
        # In _runner.py:
        services = create_auto_services(db, api.include)
        ctx["services"] = services

        # In hooks:
        async def my_hook(ctx):
            services = ctx["services"]

            # All models automatically available:
            user = await services.user.ensure_exists(...)     # Auto-generated
            tenant = await services.tenant.ensure_exists(...) # Auto-generated
            order = await services.order.ensure_exists(...)   # Auto-generated
            product = await services.product.ensure_exists(...) # Auto-generated
    """
    return AutoServiceRegistry.create_services(db, models)
