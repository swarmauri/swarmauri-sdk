# autoapi/v3/autoapi.py
from __future__ import annotations

import copy
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from .bindings.api import (
    include_model as _include_model,
    include_models as _include_models,
    rpc_call as _rpc_call,
)
from .bindings.model import rebind as _rebind, bind as _bind
from .transport import mount_jsonrpc as _mount_jsonrpc
from .system import attach_diagnostics as _attach_diagnostics
from .opspec import get_registry, OpSpec

# optional compat: legacy transactional decorator
try:
    from .compat.transactional import transactional as _txn_decorator
except Exception:  # pragma: no cover
    _txn_decorator = None


class AutoAPI:
    """
    Monolithic facade that owns:
      • containers (models, schemas, handlers, hooks, rpc, rest, routers, columns, table_config, core proxies)
      • model inclusion (REST + RPC wiring)
      • JSON-RPC / diagnostics mounting
      • (optional) legacy-friendly helpers (transactional decorator, auth flags)

    It composes v3 primitives; you can still use the functions directly if you prefer.
    """

    # --- optional auth knobs recognized by some middlewares/dispatchers (kept for back-compat) ---
    _authn: Any = None
    _allow_anon: bool = True
    _authorize: Any = None
    _optional_authn_dep: Any = None

    def __init__(
        self,
        app: Any | None = None,
        *,
        get_db: Optional[Callable[..., Any]] = None,
        get_async_db: Optional[Callable[..., Awaitable[Any]]] = None,
        jsonrpc_prefix: str = "/rpc",
        system_prefix: str = "/system",
        api_hooks: Mapping[str, Iterable[Callable]]
        | Mapping[str, Mapping[str, Iterable[Callable]]]
        | None = None,
    ) -> None:
        # host app (FastAPI or APIRouter)
        self.app = app
        # DB dependencies for transports/diagnostics
        self.get_db = get_db
        self.get_async_db = get_async_db
        self.jsonrpc_prefix = jsonrpc_prefix
        self.system_prefix = system_prefix

        # public containers (mirrors used by bindings.api)
        self.models: Dict[str, type] = {}
        self.schemas = SimpleNamespace()
        self.handlers = SimpleNamespace()
        self.hooks = SimpleNamespace()
        self.rpc = SimpleNamespace()
        self.rest = SimpleNamespace()
        self.routers: Dict[str, Any] = {}
        self.columns: Dict[str, Tuple[str, ...]] = {}
        self.table_config: Dict[str, Dict[str, Any]] = {}
        self.core = SimpleNamespace()

        # API-level hooks map (merged into each model at include-time; precedence handled in bindings.hooks)
        self._api_hooks_map = copy.deepcopy(api_hooks) if api_hooks else None

    # ------------------------- internal helpers -------------------------

    @staticmethod
    def _merge_api_hooks_into_model(model: type, hooks_map: Any) -> None:
        """
        Install API-level hooks on the model so the binder can see them.
        Accepted shapes:
            {phase: [fn, ...]}                           # global, all aliases
            {alias: {phase: [fn, ...]}, "*": {...}}      # per-alias + wildcard
        If the model already has __autoapi_api_hooks__, we shallow-merge keys.
        """
        if not hooks_map:
            return
        existing = getattr(model, "__autoapi_api_hooks__", None)
        if existing is None:
            setattr(model, "__autoapi_api_hooks__", copy.deepcopy(hooks_map))
            return

        # shallow merge (alias or phase keys); values are lists we extend
        merged = copy.deepcopy(existing)
        for k, v in (hooks_map or {}).items():
            if k not in merged:
                merged[k] = copy.deepcopy(v)
            else:
                # when both are dicts, merge phase lists
                if isinstance(v, Mapping) and isinstance(merged[k], Mapping):
                    for ph, fns in v.items():
                        merged[k].setdefault(ph, [])
                        merged[k][ph] = list(merged[k][ph]) + list(fns or [])
                else:
                    # fallback: prefer model-local value, then append api-level
                    if isinstance(merged[k], list):
                        merged[k] = list(merged[k]) + list(v or [])
                    else:
                        merged[k] = v
        setattr(model, "__autoapi_api_hooks__", merged)

    # ------------------------- primary operations -------------------------

    def include_model(
        self, model: type, *, prefix: str | None = None, mount_router: bool = True
    ) -> Tuple[type, Any]:
        """
        Bind a model, mount its REST router, and attach all namespaces to this facade.
        """
        # inject API-level hooks so the binder merges them
        self._merge_api_hooks_into_model(model, self._api_hooks_map)
        return _include_model(
            self, model, app=self.app, prefix=prefix, mount_router=mount_router
        )

    def include_models(
        self,
        models: Sequence[type],
        *,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        for m in models:
            self._merge_api_hooks_into_model(m, self._api_hooks_map)
        return _include_models(
            self,
            models,
            app=self.app,
            base_prefix=base_prefix,
            mount_router=mount_router,
        )

    async def rpc_call(
        self,
        model_or_name: type | str,
        method: str,
        payload: Any = None,
        *,
        db: Any,
        request: Any = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await _rpc_call(
            self, model_or_name, method, payload, db=db, request=request, ctx=ctx
        )

    # ------------------------- extras / mounting -------------------------

    def mount_jsonrpc(self, *, prefix: str | None = None) -> Any:
        """Mount JSON-RPC router onto `self.app`."""
        px = prefix if prefix is not None else self.jsonrpc_prefix
        return _mount_jsonrpc(
            self,
            self.app,
            prefix=px,
            get_db=self.get_db,
            get_async_db=self.get_async_db,
        )

    def attach_diagnostics(self, *, prefix: str | None = None) -> Any:
        """Mount diagnostics router onto `self.app`."""
        px = prefix if prefix is not None else self.system_prefix
        router = _attach_diagnostics(
            self, get_db=self.get_db, get_async_db=self.get_async_db
        )
        if hasattr(self.app, "include_router") and callable(self.app.include_router):
            self.app.include_router(router, prefix=px)
        return router

    # ------------------------- registry passthroughs -------------------------

    def registry(self, model: type):
        """Return the per-model OpspecRegistry."""
        return get_registry(model)

    def bind(self, model: type) -> Tuple[OpSpec, ...]:
        """Bind/rebuild a model in place (without mounting)."""
        self._merge_api_hooks_into_model(model, self._api_hooks_map)
        return _bind(model)

    def rebind(
        self, model: type, *, changed_keys: Optional[set[tuple[str, str]]] = None
    ) -> Tuple[OpSpec, ...]:
        """Targeted rebuild of a bound model."""
        return _rebind(model, changed_keys=changed_keys)

    # ------------------------- legacy helpers -------------------------

    def transactional(self, *dargs, **dkw):
        """
        Legacy-friendly decorator: @api.transactional(...)
        Wraps a function as a v3 custom op with START_TX/END_TX.
        """
        if _txn_decorator is None:
            raise RuntimeError("transactional decorator not available")
        return _txn_decorator(self, *dargs, **dkw)

    # Optional: let callers set auth knobs used by some middlewares/dispatchers
    def set_auth(
        self,
        *,
        authn: Any = None,
        allow_anon: Optional[bool] = None,
        authorize: Any = None,
        optional_authn_dep: Any = None,
    ) -> None:
        if authn is not None:
            self._authn = authn
        if allow_anon is not None:
            self._allow_anon = bool(allow_anon)
        if authorize is not None:
            self._authorize = authorize
        if optional_authn_dep is not None:
            self._optional_authn_dep = optional_authn_dep

    # ------------------------- repr -------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AutoAPI models={list(self.models)} rpc={list(getattr(self.rpc, '__dict__', {}).keys())}>"
