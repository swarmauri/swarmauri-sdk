"""ORM-backed API surface for the authentication service.

Exports
-------
Base       : Declarative base for all models in **autoapi_authn**.
metadata   : Shared SQLAlchemy ``MetaData`` with a sane naming-convention.
router     : FastAPI router combining AutoAPI resources and auth flows.
autoapi    : The ``AutoAPI`` instance used to produce *router*.

The resulting ``surface_api`` exposes a symmetrical REST/RPC surface under
namespaces like ``surface_api.core.User.create`` and
``surface_api.core_raw.User.create``.

Notes
-----
*   All mix-ins (GUIDPk, Timestamped, TenantBound, etc.) live in
    *autoapi.v3.mixins* and are imported **only** by ``tables.py``.
*   Importing this module has the side-effect of importing
    ``autoapi_authn.orm.tables``, so every model class is registered with
    the declarative base **before** AutoAPI introspects the metadata.
"""

from __future__ import annotations

from autoapi.v3 import AutoAPI
from auto_authn.orm.tables import (
    Tenant,
    User,
    Client,
    ApiKey,
    Service,
    ServiceKey,
    AuthSession,
)
from fastapi import APIRouter
from ..db import get_async_db  # same module as before
from .auth_flows import router as flows_router

# ----------------------------------------------------------------------
# 3.  Build AutoAPI instance & router
# ----------------------------------------------------------------------
surface_api = AutoAPI(
    get_async_db=get_async_db,
)

surface_api.include_models(
    [Tenant, User, Client, ApiKey, Service, ServiceKey, AuthSession]
)

router = APIRouter()
for r in surface_api.routers.values():
    router.include_router(r)
router.include_router(flows_router)
surface_api.router = router

__all__ = ["surface_api"]
