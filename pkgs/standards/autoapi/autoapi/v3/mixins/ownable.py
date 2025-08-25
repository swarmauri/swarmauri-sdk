# autoapi/v3/mixins/ownable.py
from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Mapping
from uuid import UUID

from ..columns import acol as col
from ..specs import IO, S, F, acol as spec_acol
from ..specs.storage_spec import ForeignKeySpec
from ..types import PgUUID, declared_attr
from ..runtime.errors import create_standardized_error
from ..config.constants import (
    AUTOAPI_HOOKS_ATTR,
    AUTOAPI_OWNER_POLICY_ATTR,
    CTX_AUTH_KEY,
    CTX_USER_ID_KEY,
)

log = logging.getLogger(__name__)


class OwnerPolicy(str, Enum):
    CLIENT_SET = "client"  # client may set; validated against user_id if provided
    DEFAULT_TO_USER = "default"  # if missing, default to user_id
    STRICT_SERVER = "strict"  # server enforces user_id; client cannot override


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


def _is_missing(v: Any) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def _normalize_uuid(v: Any) -> Any:
    if isinstance(v, UUID):
        return v
    if isinstance(v, str):
        try:
            return UUID(v)
        except ValueError:
            return v
    return v


def _ctx_user_id(ctx: Mapping[str, Any]) -> Any | None:
    """
    Best-effort extraction of the caller user_id from ctx.
    Checks:
      1) ctx["user_id"] (preferred in v3)
      2) ctx["auth"]["user_id"] (v3 conventional)
      3) ctx["injected_fields"]["user_id"] (legacy)
      4) ctx["auth_context"]["user_id"] (legacy)
    """
    # 1) direct
    u = (
        ctx.get(CTX_USER_ID_KEY)
        if isinstance(ctx, dict)
        else getattr(ctx, CTX_USER_ID_KEY, None)
    )
    if u:
        return _normalize_uuid(u)

    # 2) auth dict
    auth = (
        ctx.get(CTX_AUTH_KEY)
        if isinstance(ctx, dict)
        else getattr(ctx, CTX_AUTH_KEY, None)
    ) or {}
    u = auth.get("user_id")
    if u:
        return _normalize_uuid(u)

    # 3 & 4) legacy fallbacks
    inj = (
        ctx.get("injected_fields")
        if isinstance(ctx, dict)
        else getattr(ctx, "injected_fields", None)
    ) or {}
    u = inj.get("user_id")
    if u:
        return _normalize_uuid(u)

    ac = (
        ctx.get("auth_context")
        if isinstance(ctx, dict)
        else getattr(ctx, "auth_context", None)
    ) or {}
    u = ac.get("user_id")
    if u:
        return _normalize_uuid(u)

    return None


class Ownable:
    """
    Mixin that adds an `owner_id` column and installs v3 hooks to enforce ownership policy.

    Policy (per `__autoapi_owner_policy__`):
      • CLIENT_SET:       client may provide `owner_id`; if missing, we leave it as-is.
      • DEFAULT_TO_USER:  if `owner_id` missing, default to ctx user; if provided, keep it.
      • STRICT_SERVER:    always enforce `owner_id = ctx user`; reject mismatches.

    Hooks (installed at class creation via __init_subclass__):
      • PRE_TX_BEGIN on "create": normalize/enforce `owner_id` in ctx.env.params & ctx.payload
      • PRE_TX_BEGIN on "update": forbid changing `owner_id` unless CLIENT_SET and matches ctx user
        (note: if you need to compare with the existing DB value, do that in POST_HANDLER where
         your core sets ctx["result"] or fetch the row here — this version validates intent only)
    """

    __autoapi_owner_policy__: OwnerPolicy = OwnerPolicy.CLIENT_SET

    @declared_attr
    def owner_id(cls):
        pol = getattr(cls, AUTOAPI_OWNER_POLICY_ATTR, OwnerPolicy.CLIENT_SET)
        schema = _infer_schema(cls, default="public")

        storage = S(
            type_=PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target=f"{schema}.users.id"),
            nullable=False,
            index=True,
        )
        field = F(py_type=UUID)
        if pol == OwnerPolicy.CLIENT_SET:
            io = IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                mutable_verbs=("create", "update", "replace"),
            )
        else:
            io = IO(out_verbs=("read", "list"))

        return col(spec=spec_acol(storage=storage, field=field, io=io))

    # ── hook installers --------------------------------------------------------

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._install_ownable_hooks()

    @classmethod
    def _install_ownable_hooks(cls) -> None:
        """
        Attach PRE_TX_BEGIN hooks to the class under __autoapi_hooks__.

        Structure expected by v3 binder:
            {
              "<alias>": {
                 "PRE_TX_BEGIN": [callable, ...],
                 ...
              },
              ...
            }
        """

        def _err(status: int, msg: str):
            http_exc, _, _ = create_standardized_error(status, message=msg)
            raise http_exc

        def _before_create(ctx: dict[str, Any]) -> None:
            params = (ctx.get("env") or {}).get("params") or ctx.get("payload") or {}
            if hasattr(params, "model_dump"):
                params = params.model_dump()

            user_id = _ctx_user_id(ctx)
            provided = params.get("owner_id")
            missing = _is_missing(provided)
            pol = getattr(cls, AUTOAPI_OWNER_POLICY_ATTR, OwnerPolicy.CLIENT_SET)

            log.debug(
                "Ownable PRE_TX_BEGIN(create): policy=%s params=%s user_id=%s",
                pol,
                params,
                user_id,
            )

            if pol == OwnerPolicy.STRICT_SERVER:
                if user_id is None:
                    _err(400, "owner_id is required.")
                if not missing and _normalize_uuid(provided) != _normalize_uuid(
                    user_id
                ):
                    _err(400, "owner_id mismatch.")
                params["owner_id"] = user_id  # always enforce server value
            elif pol == OwnerPolicy.DEFAULT_TO_USER:
                if missing and user_id is not None:
                    params["owner_id"] = user_id
                elif not missing:
                    params["owner_id"] = _normalize_uuid(provided)
            else:  # CLIENT_SET
                if not missing:
                    params["owner_id"] = _normalize_uuid(provided)
                # if missing, leave as-is (schema/DB may enforce NOT NULL)

            # write back into both env.params and payload so downstream sees the same view
            if "env" in ctx and ctx["env"] is not None:
                ctx["env"].params = params
            ctx["payload"] = params

        def _before_update(ctx: dict[str, Any]) -> None:
            params = (ctx.get("env") or {}).get("params") or ctx.get("payload") or {}
            if hasattr(params, "model_dump"):
                params = params.model_dump()

            if "owner_id" not in params:
                return  # nothing to check

            pol = getattr(cls, AUTOAPI_OWNER_POLICY_ATTR, OwnerPolicy.CLIENT_SET)
            if _is_missing(params.get("owner_id")):
                # treat None/"" as not provided → drop it
                params.pop("owner_id", None)
                if "env" in ctx and ctx["env"] is not None:
                    ctx["env"].params = params
                ctx["payload"] = params
                return

            if pol != OwnerPolicy.CLIENT_SET:
                _err(400, "owner_id is immutable.")

            # CLIENT_SET: require new value == caller user_id unless an admin flag is present
            new_val = _normalize_uuid(params["owner_id"])
            user_id = _ctx_user_id(ctx)
            is_admin = bool(ctx.get("is_admin"))

            log.debug(
                "Ownable PRE_TX_BEGIN(update): new=%s user_id=%s is_admin=%s",
                new_val,
                user_id,
                is_admin,
            )

            if not is_admin and user_id is not None and new_val != user_id:
                _err(403, "Cannot transfer ownership.")

            # normalize stored value
            params["owner_id"] = new_val
            if "env" in ctx and ctx["env"] is not None:
                ctx["env"].params = params
            ctx["payload"] = params

        # Attach (merge) into __autoapi_hooks__ without clobbering existing mappings
        hooks = getattr(cls, AUTOAPI_HOOKS_ATTR, None) or {}
        hooks = {**hooks}  # shallow copy

        def _append(alias: str, phase: str, fn):
            phase_map = hooks.get(alias) or {}
            lst = list(phase_map.get(phase) or [])
            if fn not in lst:
                lst.append(fn)
            phase_map[phase] = tuple(
                lst
            )  # tuples are safer against accidental mutation
            hooks[alias] = phase_map

        _append("create", "PRE_TX_BEGIN", _before_create)
        _append("update", "PRE_TX_BEGIN", _before_update)

        setattr(cls, AUTOAPI_HOOKS_ATTR, hooks)
