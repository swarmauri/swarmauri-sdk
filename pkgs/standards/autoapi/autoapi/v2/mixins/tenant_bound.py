"""
Tenant-level row security mix-in for AutoAPI.

A table that inherits **TenantBound** gets:

• tenant-scoped *read* / *list* results (via _RowBound.is_visible override)
• automatic injection of the authenticated tenant id on inserts
• policy-driven control over whether the client can set / patch tenant_id
"""

from enum import Enum
import logging

from ._RowBound import _RowBound
from ..types import Column, ForeignKey, PgUUID, declared_attr
from ..hooks import Phase
from ..jsonrpc_models import create_standardized_error
from ..info_schema import check as _info_check


log = logging.getLogger(__name__)


class TenantPolicy(str, Enum):
    CLIENT_SET = "client"  # client may supply tenant_id on create/update
    DEFAULT_TO_CTX = "default"  # server fills tenant_id on create; immutable
    STRICT_SERVER = "strict"  # server forces tenant_id and forbids changes


class TenantBound(_RowBound):
    """
    Plug-and-play tenant isolation.

    • `tenant_id` column is defined per subclass (declared_attr) so the schema
      builder sees the right flags before caching.
    • _RowBound’s read/list filters work because we implement `is_visible`.
    """

    __autoapi_tenant_policy__: TenantPolicy = TenantPolicy.CLIENT_SET

    # ────────────────────────────────────────────────────────────────────
    # tenant_id column
    # -------------------------------------------------------------------
    @declared_attr
    def tenant_id(cls):
        pol = getattr(cls, "__autoapi_tenant_policy__", TenantPolicy.CLIENT_SET)

        autoapi_meta: dict[str, object] = {}
        if pol != TenantPolicy.CLIENT_SET:
            # Hide field on *all* write verbs and mark as read-only
            autoapi_meta["disable_on"] = ["update", "replace"]
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
    # Row-level visibility for _RowBound
    # -------------------------------------------------------------------
    @staticmethod
    def is_visible(obj, ctx) -> bool:
        """
        A row is visible iff it belongs to the caller’s tenant.
        The tenant id is provided via ``__autoapi_injected_fields__``.
        """
        auto_fields = ctx.get("__autoapi_injected_fields__", {})
        ctx_tenant_id = auto_fields.get("tenant_id")
        return getattr(obj, "tenant_id", None) == ctx_tenant_id

    # -------------------------------------------------------------------
    # Runtime hooks (needs api instance)
    # -------------------------------------------------------------------
    @classmethod
    def __autoapi_register_hooks__(cls, api):
        pol = cls.__autoapi_tenant_policy__

        def _err(code: int, msg: str):
            http_exc, _, _ = create_standardized_error(code, message=msg)
            raise http_exc

        # INSERT
        def _tenantbound_before_create(ctx):
            params = ctx["env"].params if ctx.get("env") else {}
            if hasattr(params, "model_dump"):
                params = params.model_dump()
            auto_fields = ctx.get("__autoapi_injected_fields__", {})
            tenant_id = auto_fields.get("tenant_id")
            log.debug(
                "TenantBound before_create policy=%s params=%s auto_fields=%s",
                pol,
                params,
                auto_fields,
            )
            if pol == TenantPolicy.STRICT_SERVER:
                if tenant_id is None:
                    _err(400, "tenant_id is required.")
                if "tenant_id" in params and params["tenant_id"] not in (
                    None,
                    tenant_id,
                ):
                    _err(400, "tenant_id mismatch.")
                if "tenant_id" in auto_fields or "tenant_id" not in params:
                    params["tenant_id"] = tenant_id
            else:
                if "tenant_id" not in params:
                    if tenant_id is None:
                        _err(400, "tenant_id is required.")
                    params["tenant_id"] = tenant_id
            ctx["env"].params = params

        # UPDATE
        def _tenantbound_before_update(ctx, obj):
            params = getattr(ctx.get("env"), "params", None)
            if not params or "tenant_id" not in params:
                return
            if pol != TenantPolicy.CLIENT_SET:
                _err(400, "tenant_id is immutable.")
            new_val = params["tenant_id"]
            auto_fields = ctx.get("__autoapi_injected_fields__", {})
            tenant_id = auto_fields.get("tenant_id")
            log.debug(
                "TenantBound before_update new_val=%s obj_tid=%s injected=%s",
                new_val,
                getattr(obj, "tenant_id", None),
                tenant_id,
            )
            if (
                new_val != obj.tenant_id
                and new_val != tenant_id
                and not ctx.get("is_admin")
            ):
                _err(403, "Cannot switch tenant context.")

        # Register hooks
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="create")(
            _tenantbound_before_create
        )
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="update")(
            _tenantbound_before_update
        )
