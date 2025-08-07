"""
Tenant-level row security mix-in for AutoAPI.

Any model that inherits **TenantBound** gains:

• automatic scoping of *read* / *list* results to ctx.tenant_id (via _RowBound)
• server-side injection of ctx.tenant_id on insert
• selectable policy for whether clients may set / patch tenant_id
"""

from enum import Enum

from ._RowBound import _RowBound
from ..types import Column, ForeignKey, PgUUID, declared_attr
from ..hooks import Phase
from ..jsonrpc_models import create_standardized_error
from ..info_schema import check as _info_check


class TenantPolicy(str, Enum):
    CLIENT_SET = "client"  # client may supply tenant_id on create/update
    DEFAULT_TO_CTX = "default"  # server fills tenant_id on create; immutable
    STRICT_SERVER = "strict"  # server forces tenant_id and forbids changes


class TenantBound(_RowBound):
    """
    Mix-in that plugs tenant isolation into AutoAPI.

    • Column metadata is produced with @declared_attr, so the schema builder
      sees the correct flags before caching.
    • _RowBound supplies the read/list visibility filter; we only need to
      point it at the right column.
    """

    __autoapi_tenant_policy__: TenantPolicy = TenantPolicy.CLIENT_SET

    # ────────────────────────────────────────────────────────────────────
    # Column definition (per-subclass)
    # -------------------------------------------------------------------
    @declared_attr
    def tenant_id(cls):
        pol = getattr(cls, "__autoapi_tenant_policy__", TenantPolicy.CLIENT_SET)

        autoapi_meta = {}
        if pol != TenantPolicy.CLIENT_SET:
            # Hide field on write verbs and mark as read-only
            autoapi_meta["disable_on"] = [
                "update",
                "replace",
            ]  # add "create" if desired
            autoapi_meta["read_only"] = True

        _info_check(autoapi_meta, "tenant_id", cls.__name__)

        return Column(
            PgUUID,
            ForeignKey("tenants.id"),
            nullable=False,
            index=True,
            info={"autoapi": autoapi_meta} if autoapi_meta else {},
        )

    # -------------------------------------------------------------------
    # Tell _RowBound which FK to use for visibility filtering
    # -------------------------------------------------------------------
    @classmethod
    def _bound_column(cls):
        return cls.tenant_id

    # -------------------------------------------------------------------
    # Runtime hooks (needs api instance)
    # -------------------------------------------------------------------
    @classmethod
    def __autoapi_register_hooks__(cls, api, concrete_model=None):
        # Use the concrete model if provided, otherwise fall back to cls
        target_model = concrete_model if concrete_model is not None else cls
        pol = getattr(
            target_model, "__autoapi_tenant_policy__", cls.__autoapi_tenant_policy__
        )

        def _err(code: int, msg: str):
            http_exc, _, _ = create_standardized_error(code, detail=msg)
            raise http_exc

        # INSERT logic
        def _before_create(ctx):
            if "tenant_id" in ctx.params and pol == TenantPolicy.STRICT_SERVER:
                _err(400, "tenant_id cannot be set explicitly.")
            ctx.params.setdefault("tenant_id", ctx.tenant_id)

        # UPDATE logic
        def _before_update(ctx, obj):
            if "tenant_id" not in ctx.params:
                return
            if pol != TenantPolicy.CLIENT_SET:
                _err(400, "tenant_id is immutable.")
            new_val = ctx.params["tenant_id"]
            if (
                new_val != obj.tenant_id
                and new_val != ctx.tenant_id
                and not ctx.is_admin
            ):
                _err(403, "Cannot switch tenant context.")

        # Register hooks
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="create")(
            _before_create
        )
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="update")(
            _before_update
        )
