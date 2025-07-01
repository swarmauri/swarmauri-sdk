"""peagen.db.api.v1.main
=======================

• Discovers ORM components that have matching Pydantic schemas.
• Generates CRUD routers (SQLAlchemy by default) and bundles them
  under a single `APIRouter` ready to be included in the FastAPI app.
"""

from __future__ import annotations

from fastapi import APIRouter

import peagen.orm as orm
import peagen.orm.schemas as orm_schemas
from peagen.db.api.v1.utils import (
    create_route_objects,
    create_routers,
    attach_list_of_routers,
)

# ----------------------------------------------------------------------
# Component discovery
# ----------------------------------------------------------------------
def _discover_components() -> list[str]:
    """
    Return base names (e.g. ``Tenant``, ``Task``) for which *all*
    of the following exist:

        • SQLAlchemy model  <Name>Model
        • Pydantic schema   <Name>
        • Pydantic schema   <Name>Create
        • Pydantic schema   <Name>Update
    """
    components: list[str] = []

    for attr in getattr(orm, "__all__", []):
        if not attr.endswith("Model"):
            continue
        base = attr[:-5]  # strip 'Model'
        if all(
            hasattr(orm_schemas, f"{base}{suffix}")
            for suffix in ("Read", "Create", "Update")
        ):
            components.append(base)

    # Optional: keep stable ordering for reproducible OpenAPI docs
    components.sort()
    return components


COMPONENTS: list[str] = _discover_components()

# ----------------------------------------------------------------------
# Router factory
# ----------------------------------------------------------------------
def get_routes() -> APIRouter:
    """
    Assemble and return an :class:`fastapi.APIRouter` containing CRUD
    endpoints for every discovered component.
    """
    router = APIRouter()

    route_specs   = create_route_objects(COMPONENTS)
    crud_routers  = create_routers(route_specs)          # SQLAlchemy by default
    attach_list_of_routers(router, crud_routers)

    return router


# Public export consumed by peagen.db.main
ROUTES = get_routes()
