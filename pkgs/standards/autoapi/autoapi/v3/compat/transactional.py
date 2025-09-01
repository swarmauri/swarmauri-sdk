from __future__ import annotations

import warnings
from typing import Any, Callable

from ..bindings.api import include_model
from ..bindings.model import bind as bind_model
from ..ops import OpSpec, get_registry
from ..schema.types import SchemaArg
from ..config.constants import AUTOAPI_TX_MODELS_ATTR


def _pascal(s: str) -> str:
    return "".join(p.capitalize() or "_" for p in s.replace("-", "_").split("_"))


def _split_name(name: str | None, fn_name: str) -> tuple[str, str]:
    """
    Return (model_scope, alias). If name has a dot, split on first dot.
    Else use 'txn' as the model scope and the function name (or provided name) as alias.
    """
    if not name:
        return ("txn", fn_name)
    if "." in name:
        a, b = name.split(".", 1)
        return (a or "txn", b or fn_name)
    return ("txn", name)


def _ensure_tx_model(api: Any, scope: str, *, resource: str | None = None) -> type:
    """
    Get or create a synthetic model class for this transactional scope.
    We keep them on api.__autoapi_tx_models__ to avoid re-creating classes.
    """
    store = getattr(api, AUTOAPI_TX_MODELS_ATTR, None)
    if store is None:
        store = {}
        setattr(api, AUTOAPI_TX_MODELS_ATTR, store)

    key = scope.lower()
    mdl = store.get(key)
    if mdl:
        return mdl

    class_name = _pascal(scope)
    # A tiny, ops-only model (no table); resource controls REST prefix
    mdl = type(
        class_name, (), {"__resource__": (resource if resource is not None else "txn")}
    )
    store[key] = mdl
    return mdl


def _normalize_rest_path(
    rest_path: str | None, name_for_default: str, alias: str
) -> str:
    """
    If rest_path is given, use it as an absolute path.
    Else default to '/<name with dots -> slashes>' to mimic v2 behavior.
    """
    if rest_path:
        path = "/" + rest_path.lstrip("/")
    else:
        path = "/" + name_for_default.replace(".", "/")
    return path


def transactional(  # noqa: D401 (compat docstring in v2)
    api: Any,
    fn: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    rest_path: str | None = None,
    rest_method: str = "POST",
    tags: tuple[str, ...] = ("txn",),
    expose_rpc: bool = True,
    expose_routes: bool = True,
    request_model: SchemaArg | None = None,
    response_model: SchemaArg | None = None,
) -> Callable[..., Any]:
    """
    v3-compatible replacement for the v2 @api.transactional decorator.

    Usage (same as v2):
        @transactional(api)
        def bundle_create(params, db): ...

        @transactional(api, name="bundle.create", rest_path="/tx/bundle", rest_method="PUT")
        async def bundle(params, db): ...
    """
    warnings.warn(
        "The transactional decorator is deprecated; prefer model-scoped OpSpecs. "
        "This shim wraps your function as a v3 custom op with START_TX/END_TX phases.",
        DeprecationWarning,
        stacklevel=2,
    )

    def _wrap(user_fn: Callable[..., Any]) -> Callable[..., Any]:
        scope, alias = _split_name(name, user_fn.__name__)
        model = _ensure_tx_model(api, scope)

        # Build an OpSpec for this transactional
        sp = OpSpec(
            alias=alias,
            target="custom",
            handler=user_fn,  # v3 handlers will pass (ctx, db, payload, request, model, op) as needed
            expose_rpc=expose_rpc,
            expose_routes=expose_routes,
            http_methods=(rest_method,),
            path_suffix=_normalize_rest_path(
                rest_path, name or user_fn.__name__, alias
            ),
            tags=tags,
            persist="always",  # ensure START_TX/END_TX are injected
            request_model=request_model,
            response_model=response_model,
        )

        # Register on the model's registry and (re)bind the model
        reg = get_registry(model)
        reg.add(sp)  # idempotent replace per-alias
        bind_model(model)  # builds schemas/hooks/handlers/rpc/rest

        # Ensure router is mounted under the API (prefix '' so our absolute path_suffix is used verbatim)
        include_model(
            api, model, app=getattr(api, "app", None), prefix="", mount_router=True
        )

        # For compatibility, return the original function (no wrapper needed)
        return user_fn

    # Support bare decorator form
    if fn is None:
        return _wrap
    return _wrap(fn)
