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
    *autoapi.v3.orm.mixins* and are imported by the ORM models.
*   Importing this module has the side-effect of importing
    ``tigrbl_auth.orm``, so every model class is registered with the
    declarative base **before** AutoAPI introspects the metadata.
"""

from __future__ import annotations

from autoapi.v3 import AutoAPI
from tigrbl_auth.orm import (
    Tenant,
    User,
    Client,
    ApiKey,
    Service,
    ServiceKey,
    AuthSession,
)
from ..db import dsn
from .auth_flows import router as flows_router

# ----------------------------------------------------------------------
# 3.  Build AutoAPI instance & router
# ----------------------------------------------------------------------
surface_api = AutoAPI(engine=dsn)

surface_api.include_models(
    [Tenant, User, Client, ApiKey, Service, ServiceKey, AuthSession]
)

surface_api.include_router(flows_router)

__all__ = ["surface_api"]
