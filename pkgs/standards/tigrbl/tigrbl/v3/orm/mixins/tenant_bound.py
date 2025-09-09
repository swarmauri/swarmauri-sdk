"""Tenant scoping mixin for Tigrbl v3."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Mapping
from uuid import UUID

from ._RowBound import _RowBound
from ...specs import acol
from ...config.constants import (
    TIGRBL_TENANT_POLICY_ATTR,
    CTX_AUTH_KEY,
    CTX_TENANT_ID_KEY,
)
from ...runtime.errors import create_standardized_error
from ...specs import ColumnSpec, F, IO, S
from ...specs.storage_spec import ForeignKeySpec
from ...types import Mapped, PgUUID, declared_attr


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
    def tenant_id(cls) -> Mapped[UUID]:
        pol = getattr(cls, TIGRBL_TENANT_POLICY_ATTR, TenantPolicy.CLIENT_SET)
        schema = _infer_schema(cls, default="public")

        in_verbs = (
            ("create", "update", "replace")
            if pol == TenantPolicy.CLIENT_SET
            else ("create",)
        )
        io = IO(
            in_verbs=in_verbs,
            out_verbs=("read", "list"),
            mutable_verbs=in_verbs,
        )

        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.tenants.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID),
            io=io,
        )
        return acol(spec=spec)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # -------------------------------------------------------------------
    # Row-level visibility for _RowBound
    # -------------------------------------------------------------------
    @staticmethod
    def is_visible(obj, ctx) -> bool:
        return getattr(obj, "tenant_id", None) == _ctx_tenant_id(ctx)

    # -------------------------------------------------------------------
    # Runtime hooks
    # -------------------------------------------------------------------
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        cls._install_tenant_bound_hooks()

    @classmethod
    def _install_tenant_bound_hooks(cls) -> None:
        pol = getattr(cls, "__tigrbl_tenant_policy__", TenantPolicy.CLIENT_SET)

        def _err(code: int, msg: str) -> None:
            http_exc, _, _ = create_standardized_error(code, message=msg)
            raise http_exc

        def _before_create(ctx: dict[str, Any]) -> None:
            env = (
                ctx.get("env") if isinstance(ctx, dict) else getattr(ctx, "env", None)
            ) or {}
            params = (
                (
                    env.get("params")
                    if isinstance(env, dict)
                    else getattr(env, "params", None)
                )
                or (
                    ctx.get("payload")
                    if isinstance(ctx, dict)
                    else getattr(ctx, "payload", None)
                )
                or {}
            )
            if hasattr(params, "model_dump"):
                params = params.model_dump()

            tenant_id = _ctx_tenant_id(ctx)
            provided = params.get("tenant_id")
            missing = _is_missing(provided)

            if pol == TenantPolicy.STRICT_SERVER:
                if tenant_id is None:
                    _err(400, "tenant_id is required.")
                if not missing:
                    if _normalize_uuid(provided) != _normalize_uuid(tenant_id):
                        _err(400, "tenant_id mismatch.")
                    _err(400, "tenant_id is server-assigned.")
                params["tenant_id"] = tenant_id
            elif pol == TenantPolicy.DEFAULT_TO_CTX:
                if missing and tenant_id is not None:
                    params["tenant_id"] = tenant_id
                elif not missing:
                    params["tenant_id"] = _normalize_uuid(provided)
            else:  # CLIENT_SET
                if not missing:
                    params["tenant_id"] = _normalize_uuid(provided)

            env_attr = (
                ctx.get("env") if isinstance(ctx, dict) else getattr(ctx, "env", None)
            )
            if env_attr is not None:
                if isinstance(env_attr, dict):
                    env_attr["params"] = params
                else:
                    env_attr.params = params
            if isinstance(ctx, dict):
                ctx["payload"] = params
            else:
                setattr(ctx, "payload", params)

        def _before_update(ctx: dict[str, Any]) -> None:
            env = (
                ctx.get("env") if isinstance(ctx, dict) else getattr(ctx, "env", None)
            ) or {}
            params = (
                (
                    env.get("params")
                    if isinstance(env, dict)
                    else getattr(env, "params", None)
                )
                or (
                    ctx.get("payload")
                    if isinstance(ctx, dict)
                    else getattr(ctx, "payload", None)
                )
                or {}
            )
            if hasattr(params, "model_dump"):
                params = params.model_dump()

            if "tenant_id" not in params:
                return

            if _is_missing(params.get("tenant_id")):
                params.pop("tenant_id", None)
                env_attr = (
                    ctx.get("env")
                    if isinstance(ctx, dict)
                    else getattr(ctx, "env", None)
                )
                if env_attr is not None:
                    if isinstance(env_attr, dict):
                        env_attr["params"] = params
                    else:
                        env_attr.params = params
                if isinstance(ctx, dict):
                    ctx["payload"] = params
                else:
                    setattr(ctx, "payload", params)
                return

            if pol != TenantPolicy.CLIENT_SET:
                _err(400, "tenant_id is immutable.")

            new_val = _normalize_uuid(params["tenant_id"])
            tenant_id = _ctx_tenant_id(ctx)
            is_admin = bool(ctx.get("is_admin"))

            if not is_admin and tenant_id is not None and new_val != tenant_id:
                _err(403, "Cannot switch tenant context.")

            params["tenant_id"] = new_val
            env_attr = (
                ctx.get("env") if isinstance(ctx, dict) else getattr(ctx, "env", None)
            )
            if env_attr is not None:
                if isinstance(env_attr, dict):
                    env_attr["params"] = params
                else:
                    env_attr.params = params
            if isinstance(ctx, dict):
                ctx["payload"] = params
            else:
                setattr(ctx, "payload", params)

        hooks = {**getattr(cls, "__tigrbl_hooks__", {})}

        def _append(alias: str, phase: str, fn) -> None:
            phase_map = hooks.get(alias) or {}
            lst = list(phase_map.get(phase) or [])
            if fn not in lst:
                lst.append(fn)
            phase_map[phase] = tuple(lst)
            hooks[alias] = phase_map

        _append("create", "PRE_TX_BEGIN", _before_create)
        _append("update", "PRE_TX_BEGIN", _before_update)

        setattr(cls, "__tigrbl_hooks__", hooks)


def _ctx_tenant_id(ctx: Mapping[str, Any]) -> Any | None:
    """Best-effort extraction of tenant_id from ctx."""
    t = (
        ctx.get(CTX_TENANT_ID_KEY)
        if isinstance(ctx, dict)
        else getattr(ctx, CTX_TENANT_ID_KEY, None)
    )
    if t:
        return _normalize_uuid(t)

    auth = (
        ctx.get(CTX_AUTH_KEY)
        if isinstance(ctx, dict)
        else getattr(ctx, CTX_AUTH_KEY, None)
    ) or {}
    t = auth.get(CTX_TENANT_ID_KEY)
    if t:
        return _normalize_uuid(t)

    inj = (
        ctx.get("injected_fields")
        if isinstance(ctx, dict)
        else getattr(ctx, "injected_fields", None)
    ) or {}
    t = inj.get(CTX_TENANT_ID_KEY)
    if t:
        return _normalize_uuid(t)

    ac = (
        ctx.get("auth_context")
        if isinstance(ctx, dict)
        else getattr(ctx, "auth_context", None)
    ) or {}
    t = ac.get(CTX_TENANT_ID_KEY)
    if t:
        return _normalize_uuid(t)

    return None
