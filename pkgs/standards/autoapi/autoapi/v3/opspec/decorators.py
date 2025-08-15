# autoapi/v3/opspec/decorators.py
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Sequence, Type

from .types import (
    OpSpec,
    PersistPolicy,
    TargetOp,
    Arity,
    ReturnForm,
    OpHook,  # for optional hook lists passed in
)
from ..config.constants import OPS_ATTR, CUSTOM_OP_ATTR

# ───────────────────────────────────────────────────────────────────────────────
# Class-level alias decorator
# ───────────────────────────────────────────────────────────────────────────────


def op_alias(
    *,
    alias: str,
    target: TargetOp,
    arity: Arity | None = None,
    persist: PersistPolicy = "default",
    request_model: Type | None = None,
    response_model: Type | None = None,
    http_methods: Sequence[str] | None = None,
    tags: Sequence[str] | None = None,
    rbac_guard_op: TargetOp | None = None,
    # optional extras
    path_suffix: str | None = None,
    returns: ReturnForm | None = None,
    hooks: Sequence[OpHook] | None = None,
    expose_routes: bool | None = None,
    expose_rpc: bool | None = None,
    expose_method: bool | None = None,
):
    """
    Declare an alias for a canonical target on a table class.

    This attaches an OpSpec to the model (class-level). Handlers come from the
    canonical core for the target (e.g., "create", "read", "update", ...).

    Parameters
    ----------
    alias:
      Public verb name (e.g., "soft_delete", "fetch", "upsert").
    target:
      Canonical operation to alias (e.g., "delete", "read", "replace", "list", ...).
    arity:
      "member" (needs a PK) or "collection". Defaults from the target.
    persist:
      "default" (use target’s behavior), "always" (force START_TX/END_TX), or "skip".
    request_model / response_model:
      Optional Pydantic models to drive input/output shape for this alias.
      If `returns="model"` (default for non-"clear"), responses are serialized via `response_model`.
    http_methods / path_suffix / tags:
      REST customizations (e.g., `http_methods=("POST",)`, `path_suffix="/soft"`).
    rbac_guard_op:
      Gate this alias as if it were the given canonical op (e.g., guard a "fetch" alias like "read").
    hooks:
      Sequence[OpHook] to run in specific phases (e.g., PRE_HANDLER).
    expose_routes / expose_rpc / expose_method:
      Toggle exposure to REST, JSON-RPC, and class method namespace, respectively.

    Example
    -------
        from pydantic import BaseModel

        class UpdateIn(BaseModel):
            name: str | None = None

        class User(Base):
            __tablename__ = "user"

            # Map "patch" to canonical "update" for members
            @op_alias(
                alias="patch",
                target="update",
                arity="member",
                request_model=UpdateIn,
                http_methods=("PATCH",),
                path_suffix="/patch",
                tags=("users", "mutations"),
            )
            class _(Base):  # dummy inner to attach the decorator at class-level
                pass

    Produced surface
    ----------------
    • REST:   PATCH /user/{pk}/patch     (body validated with UpdateIn)
    • RPC:    method "User.patch"        (params validated with UpdateIn)
    • Phases: same as canonical "update" (PRE_HANDLER/HANDLER/POST_HANDLER, START_TX/END_TX, etc.)
    """

    def deco(table_cls: Type):
        # attach to __autoapi_ops__ without touching the imperative registry
        ops = list(getattr(table_cls, OPS_ATTR, ()))
        spec = OpSpec(
            alias=alias,
            target=target,
            table=table_cls,
            arity=arity
            or (
                "member"
                if target in {"read", "update", "replace", "delete"}
                else "collection"
            ),
            persist=persist,
            request_model=request_model,
            response_model=response_model,
            http_methods=tuple(http_methods) if http_methods else None,
            path_suffix=path_suffix,
            tags=tuple(tags) if tags else (),
            rbac_guard_op=rbac_guard_op,
            returns=returns or ("model" if target != "clear" else "raw"),
            hooks=tuple(hooks) if hooks else (),
            # exposure toggles (fall back to OpSpec defaults when None)
            expose_routes=True if expose_routes is None else bool(expose_routes),
            expose_rpc=True if expose_rpc is None else bool(expose_rpc),
            expose_method=True if expose_method is None else bool(expose_method),
        )
        ops.append(spec)
        setattr(table_cls, OPS_ATTR, tuple(ops))
        return table_cls

    return deco


# ───────────────────────────────────────────────────────────────────────────────
# Function/method-level custom op decorator
# ───────────────────────────────────────────────────────────────────────────────


def op(
    *,
    alias: str,
    arity: Arity = "collection",
    persist: PersistPolicy = "default",
    returns: ReturnForm = "model",
    request_model: Type | None = None,
    response_model: Type | None = None,
    http_methods: Sequence[str] | None = None,
    tags: Sequence[str] | None = None,
    rbac_guard_op: TargetOp | None = None,
    path_suffix: str | None = None,
    hooks: Sequence[OpHook] | None = None,
    expose_routes: bool | None = None,
    expose_rpc: bool | None = None,
    expose_method: bool | None = None,
):
    """
    Mark a method/function as a **custom** operation and attach an OpSpec.

    The collector sets `table` to the owning class and uses the decorated function
    as the **raw handler** unless you later override it. Hooks (if provided) are
    merged into the per-op phase chain.

    I/O
    ---
    • `request_model` (optional): Pydantic model to validate request body (or query for list/clear).
      The validated payload is passed to your handler as `payload: dict`.
    • `response_model` + `returns="model"`: your handler’s return value will be serialized
      through `response_model`. With `returns="raw"` we return your value as-is.

    Persistence
    -----------
    • `persist="default"` → obey model/op defaults (most ops will run START_TX/END_TX).
    • `persist="always"`  → force START_TX/END_TX injection (db.begin/db.commit).
    • `persist="skip"`    → no START_TX/END_TX (ephemeral). HANDLER phase is still flush-only.

    Handler Signature
    -----------------
    You can define the handler as an instance method or a plain function. The bindings
    adapt calls so these kwargs are available:

        async def myop(self, *, ctx, db, request, payload):
            # ctx["path_params"] holds {<real_pk_name>: value, "pk": value} for member ops
            # payload is already validated (if request_model was provided)
            ...

    REST & RPC Shapes
    -----------------
    For collection ops (no PK):
        • REST:   /<resource>/<path_suffix?>   (default method POST unless overridden)
        • RPC:    method "<Model>.<alias>", params = { ...payload... }

    For member ops (requires PK):
        • REST:   /<resource>/{pk}/<path_suffix?>
        • RPC:    method "<Model>.<alias>", params = {"pk": <id>, ...payload...}

    Examples
    --------
        from pydantic import BaseModel, Field

        class RotateIn(BaseModel):
            degrees: int = Field(ge=-360, le=360)

        class RotateOut(BaseModel):
            status: str
            applied: int

        class Wheel(Base):
            __tablename__ = "wheel"

            @custom_op(
                alias="rotate",
                arity="member",
                persist="always",          # ensure START_TX/END_TX
                returns="model",
                request_model=RotateIn,
                response_model=RotateOut,
                http_methods=("POST",),
                path_suffix="/rotate",
                tags=("wheels", "actions"),
                hooks=(),                  # optional: OpHook(...) list
                rbac_guard_op="update",    # authorize like "update"
            )
            async def rotate(self, *, ctx, db, request, payload):
                pk = ctx["path_params"]["id"]   # or your real PK name
                deg = payload["degrees"]
                # ... do stuff; may flush; commit happens in END_TX if persist != "skip"
                return {"status": "ok", "applied": deg}

    JSON-RPC call
    -------------
        # member op → include pk inside params
        {
          "jsonrpc": "2.0",
          "method":  "Wheel.rotate",
          "params":  {"pk": 123, "degrees": 90},
          "id": 1
        }

    REST call
    ---------
        POST /wheel/123/rotate
        Content-Type: application/json

        {"degrees": 90}
    """

    def deco(fn: Callable[..., Any]):
        @wraps(fn)
        def _raw(*a, **kw):
            # executor can await return values; keep wrapper sync-friendly
            return fn(*a, **kw)

        # Stash an OpSpec shell; binder/collector will set table and handler.
        setattr(
            _raw,
            CUSTOM_OP_ATTR,
            OpSpec(  # type: ignore[attr-defined]
                alias=alias,
                target="custom",
                table=None,
                arity=arity,
                persist=persist,
                returns=returns,
                handler=None,  # collector will set to the decorated function if still None
                request_model=request_model,
                response_model=response_model,
                http_methods=tuple(http_methods) if http_methods else None,
                path_suffix=path_suffix,
                tags=tuple(tags) if tags else (),
                rbac_guard_op=rbac_guard_op,
                hooks=tuple(hooks) if hooks else (),
                expose_routes=True if expose_routes is None else bool(expose_routes),
                expose_rpc=True if expose_rpc is None else bool(expose_rpc),
                expose_method=True if expose_method is None else bool(expose_method),
            ),
        )
        return _raw

    return deco


__all__ = ["op_alias", "op"]
