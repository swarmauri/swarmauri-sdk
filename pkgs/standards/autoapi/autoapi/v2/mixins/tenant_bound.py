"""
Tenant-level row security for AutoAPI.

Drop this mix-in next to `_RowBound` and `Ownable`.  Any table that inherits
`TenantBound` will automatically:

• hide `tenant_id` on create/patch if the policy is STRICT
• inject ctx.tenant_id during inserts
• scope every read/list/query to ctx.tenant_id via _RowBound
"""

from enum import Enum
from ._RowBound import _RowBound                 # ← base helper
from ..types import Column, ForeignKey, PgUUID
from ..hooks import Phase
from ..jsonrpc_models import create_standardized_error
from ..info_schema import check as _info_check


class TenantPolicy(str, Enum):
    CLIENT_SET      = "client"   # client may supply tenant_id on create/update
    DEFAULT_TO_CTX  = "default"  # server fills tenant_id on create; immutable
    STRICT_SERVER   = "strict"   # server forces tenant_id and forbids changes


class TenantBound(_RowBound):
    """
    Inherit this mix-in **and** `_RowBound` functionality is activated
    automatically because we override `_bound_column()` below.
    """

    tenant_id = Column(
        PgUUID,
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
        info={},                     # autoapi flags filled in __init_subclass__
    )
    __autoapi_tenant_policy__: TenantPolicy = TenantPolicy.CLIENT_SET

    # --------------------------------------------------------------------- #
    # Tell _RowBound which column carries the “row key”                     #
    # --------------------------------------------------------------------- #
    @classmethod
    def _bound_column(cls):        # required by _RowBound
        return cls.tenant_id

    # --------------------------------------------------------------------- #
    # ①  Column-level schema hints are set at *class-definition* time       #
    # --------------------------------------------------------------------- #
    @classmethod
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)

        pol = getattr(cls, "__autoapi_tenant_policy__", TenantPolicy.CLIENT_SET)

        meta = cls.tenant_id.info.setdefault("autoapi", {})
        if pol != TenantPolicy.CLIENT_SET:
            disables = set(meta.get("disable_on", []))
            disables.update({"update", "replace"})
            meta["disable_on"] = list(disables)
            meta.setdefault("read_only", True)

        _info_check(meta, "tenant_id", cls.__name__)   # validate keys

    # --------------------------------------------------------------------- #
    # ②  Runtime hooks (needs the api instance)                             #
    # --------------------------------------------------------------------- #
    @classmethod
    def __autoapi_register_hooks__(cls, api):
        pol = cls.__autoapi_tenant_policy__

        def _err(code: int, msg: str):
            http_exc, _, _ = create_standardized_error(code, detail=msg)
            raise http_exc

        # inject / validate on INSERT
        def _before_create(ctx):
            if "tenant_id" in ctx.params and pol == TenantPolicy.STRICT_SERVER:
                _err(400, "tenant_id cannot be set explicitly.")
            ctx.params.setdefault("tenant_id", ctx.tenant_id)

        # validate on UPDATE
        def _before_update(ctx, obj):
            if "tenant_id" not in ctx.params:
                return
            if pol != TenantPolicy.CLIENT_SET:
                _err(400, "tenant_id is immutable.")
            # optional: prohibit cross-tenant re-assignment even for CLIENT_SET
            new_val = ctx.params["tenant_id"]
            if new_val != obj.tenant_id and new_val != ctx.tenant_id and not ctx.is_admin:
                _err(403, "Cannot switch tenant context.")

        # _RowBound already registers the SELECT/LIST filter for us.
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="create")(
            _before_create
        )
        api.register_hook(model=cls, phase=Phase.PRE_TX_BEGIN, op="update")(
            _before_update
        )
