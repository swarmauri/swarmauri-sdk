from enum import Enum
import logging
from uuid import UUID

from ._RowBound import _RowBound
from ..types import Column, ForeignKey, PgUUID, declared_attr
from ..hooks import Phase
from ..jsonrpc_models import create_standardized_error
from ..info_schema import check as _info_check
from ..cfgs import AUTH_CONTEXT_KEY, INJECTED_FIELDS_KEY, TENANT_ID_KEY

log = logging.getLogger(__name__)


class TenantPolicy(str, Enum):
    CLIENT_SET = "client"  # client may supply tenant_id on create/update
    DEFAULT_TO_CTX = "default"  # server fills tenant_id on create; immutable
    STRICT_SERVER = "strict"  # server forces tenant_id and forbids changes


def _infer_schema(cls, default: str = "public") -> str:
    args = getattr(cls, "__table_args__", None)
    if not args:
        return default
    if isinstance(args, dict):
        return args.get("schema", default)
    if isinstance(args, (tuple, list)):
        for elem in args:
            if isinstance(elem, dict) and "schema" in elem:
                return elem["schema"]
    return default


def _is_missing(value) -> bool:
    """Treat None or empty strings as 'not provided'."""
    return value is None or (isinstance(value, str) and not value.strip())


def _normalize_uuid(val):
    if isinstance(val, UUID):
        return val
    if isinstance(val, str):
        try:
            return UUID(val)
        except ValueError:
            return val  # let model validation surface the error
    return val


class TenantBound(_RowBound):
    """
    Plug-and-play tenant isolation.

    • tenant_id column is defined per subclass (declared_attr) so the schema
      builder sees the right flags before caching.
    • _RowBound’s read/list filters work because we implement `is_visible`.
    """

    __tigrbl_tenant_policy__: TenantPolicy = TenantPolicy.CLIENT_SET

    # ────────────────────────────────────────────────────────────────────
    # tenant_id column (Schema-Aware; PgUUID(as_uuid=True))
    # -------------------------------------------------------------------
    @declared_attr
    def tenant_id(cls):
        pol = getattr(cls, "__tigrbl_tenant_policy__", TenantPolicy.CLIENT_SET)
        schema = _infer_schema(cls, default="public")

        tigrbl_meta: dict[str, object] = {}
        if pol != TenantPolicy.CLIENT_SET:
            tigrbl_meta["disable_on"] = ["update", "replace"]
            tigrbl_meta["read_only"] = True
        _info_check(tigrbl_meta, "tenant_id", cls.__name__)

        return Column(
            PgUUID(as_uuid=True),
            ForeignKey(f"{schema}.tenants.id"),
            nullable=False,
            index=True,
            info={"tigrbl": tigrbl_meta} if tigrbl_meta else {},
        )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # -------------------------------------------------------------------
    # Row-level visibility for _RowBound
    # -------------------------------------------------------------------
    @staticmethod
    def is_visible(obj, ctx) -> bool:
        auto_fields = ctx.get(AUTH_CONTEXT_KEY, {})
        ctx_tenant_id = auto_fields.get(TENANT_ID_KEY)
        return getattr(obj, "tenant_id", None) == ctx_tenant_id

    # -------------------------------------------------------------------
    # Runtime hooks (needs api instance)
    # -------------------------------------------------------------------
    @classmethod
    def __tigrbl_register_hooks__(cls, api):
        pol = cls.__tigrbl_tenant_policy__

        def _err(code: int, msg: str):
            http_exc, _, _ = create_standardized_error(code, message=msg)
            raise http_exc

        # INSERT
        def _tenantbound_before_create(ctx):
            params = ctx["env"].params if ctx.get("env") else {}
            if hasattr(params, "model_dump"):
                # IMPORTANT: if you DON'T do #2 below, keep exclude_none=False here,
                # and rely on _is_missing() to decide.
                params = params.model_dump()

            auto_fields = ctx.get(INJECTED_FIELDS_KEY, {})
            print(f"\n🚧{auto_fields}")
            injected_tid = auto_fields.get(TENANT_ID_KEY)
            print(f"\n🚧🚧{injected_tid}")
            provided = params.get("tenant_id")
            missing = _is_missing(provided)
            print(f"\n🚧🚧🚧{provided}")
            if cls.__tigrbl_tenant_policy__ == TenantPolicy.STRICT_SERVER:
                if injected_tid is None:
                    _err(400, "tenant_id is required.")
                if not missing and _normalize_uuid(provided) != _normalize_uuid(
                    injected_tid
                ):
                    _err(400, "tenant_id mismatch.")
                params["tenant_id"] = injected_tid
            else:
                if missing:
                    if injected_tid is None:
                        _err(400, "tenant_id is required.")
                    params["tenant_id"] = injected_tid
                else:
                    params["tenant_id"] = _normalize_uuid(provided)

            ctx["env"].params = params
            print(f"\n🚧 tenantbound params: {ctx['env'].params}")

        # UPDATE
        def _tenantbound_before_update(ctx, obj):
            params = getattr(ctx.get("env"), "params", None)
            if not params or "tenant_id" not in params:
                return

            provided = params.get("tenant_id")
            if _is_missing(provided):
                # treat None/empty as not provided → drop and ignore
                params.pop("tenant_id", None)
                ctx["env"].params = params
                return

            if pol != TenantPolicy.CLIENT_SET:
                _err(400, "tenant_id is immutable.")

            new_val = _normalize_uuid(provided)
            auto_fields = ctx.get(INJECTED_FIELDS_KEY, {})
            injected_tid = _normalize_uuid(auto_fields.get(TENANT_ID_KEY))

            log.info(
                "TenantBound before_update new_val=%s obj_tid=%s injected=%s",
                new_val,
                getattr(obj, "tenant_id", None),
                injected_tid,
            )

            if (
                new_val != obj.tenant_id
                and new_val != injected_tid
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
