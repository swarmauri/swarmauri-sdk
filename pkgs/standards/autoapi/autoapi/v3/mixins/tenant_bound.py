from enum import Enum
import logging
from uuid import UUID

from ._RowBound import _RowBound
from ..types import Column, ForeignKey, PgUUID, declared_attr
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

    __autoapi_tenant_policy__: TenantPolicy = TenantPolicy.CLIENT_SET

    # ────────────────────────────────────────────────────────────────────
    # tenant_id column (Schema-Aware; PgUUID(as_uuid=True))
    # -------------------------------------------------------------------
    @declared_attr
    def tenant_id(cls):
        pol = getattr(cls, "__autoapi_tenant_policy__", TenantPolicy.CLIENT_SET)
        schema = _infer_schema(cls, default="public")

        autoapi_meta: dict[str, object] = {}
        if pol != TenantPolicy.CLIENT_SET:
            autoapi_meta["disable_on"] = ["update", "replace"]
            autoapi_meta["read_only"] = True
        _info_check(autoapi_meta, "tenant_id", cls.__name__)

        return Column(
            PgUUID(as_uuid=True),
            ForeignKey(f"{schema}.tenants.id"),
            nullable=False,
            index=True,
            info={"autoapi": autoapi_meta} if autoapi_meta else {},
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

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._install_tenant_hooks()

    @classmethod
    def _install_tenant_hooks(cls) -> None:
        pol = cls.__autoapi_tenant_policy__

        def _err(code: int, msg: str):
            http_exc, _, _ = create_standardized_error(code, message=msg)
            raise http_exc

        def _tenantbound_before_create(ctx):
            params = ctx["env"].params if ctx.get("env") else {}
            if hasattr(params, "model_dump"):
                params = params.model_dump()
            auto_fields = ctx.get(INJECTED_FIELDS_KEY, {})
            injected_tid = auto_fields.get(TENANT_ID_KEY)
            provided = params.get("tenant_id")
            missing = _is_missing(provided)
            if cls.__autoapi_tenant_policy__ == TenantPolicy.STRICT_SERVER:
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

        def _tenantbound_before_update(ctx):
            params = getattr(ctx.get("env"), "params", None)
            if not params or "tenant_id" not in params:
                return
            provided = params.get("tenant_id")
            if _is_missing(provided):
                params.pop("tenant_id", None)
                ctx["env"].params = params
                return
            if pol != TenantPolicy.CLIENT_SET:
                _err(400, "tenant_id is immutable.")
            new_val = _normalize_uuid(provided)
            auto_fields = ctx.get(INJECTED_FIELDS_KEY, {})
            injected_tid = _normalize_uuid(auto_fields.get(TENANT_ID_KEY))
            obj = ctx.get("obj")
            log.info(
                "TenantBound before_update new_val=%s obj_tid=%s injected=%s",
                new_val,
                getattr(obj, "tenant_id", None) if obj is not None else None,
                injected_tid,
            )
            if (
                obj is not None
                and new_val != getattr(obj, "tenant_id", None)
                and new_val != injected_tid
                and not ctx.get("is_admin")
            ):
                _err(403, "Cannot switch tenant context.")

        hooks = getattr(cls, "__autoapi_hooks__", None) or {}
        hooks = {**hooks}

        def _append(alias: str, fn):
            phase_map = hooks.get(alias) or {}
            lst = list(phase_map.get("PRE_TX_BEGIN") or [])
            if fn not in lst:
                lst.append(fn)
            phase_map["PRE_TX_BEGIN"] = tuple(lst)
            hooks[alias] = phase_map

        _append("create", _tenantbound_before_create)
        _append("update", _tenantbound_before_update)
        setattr(cls, "__autoapi_hooks__", hooks)
