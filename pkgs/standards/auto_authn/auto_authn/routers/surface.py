"""ORM-backed API surface for the authentication service.

Exports
-------
Base       : Declarative base for all models in **tigrbl_authn**.
metadata   : Shared SQLAlchemy ``MetaData`` with a sane naming-convention.
router     : FastAPI router combining Tigrbl resources and auth flows.
tigrbl    : The ``Tigrbl`` instance used to produce *router*.

The resulting ``surface_api`` exposes a symmetrical REST/RPC surface under
namespaces like ``surface_api.core.User.create`` and
``surface_api.core_raw.User.create``.

Notes
-----
*   All mix-ins (GUIDPk, Timestamped, TenantBound, etc.) live in
    *tigrbl.v3.orm.mixins* and are imported by the ORM models.
*   Importing this module has the side-effect of importing
    ``auto_authn.orm``, so every model class is registered with the
    declarative base **before** Tigrbl introspects the metadata.
"""

from __future__ import annotations

from tigrbl.v3 import Tigrbl
from auto_authn.orm import (
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
# 3.  Build Tigrbl instance & router
# ----------------------------------------------------------------------
surface_api = Tigrbl(engine=dsn)

surface_api.include_models(
    [Tenant, User, Client, ApiKey, Service, ServiceKey, AuthSession]
)

surface_api.include_router(flows_router)

__all__ = ["surface_api"]
