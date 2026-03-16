from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict, Mapping, Optional

from tigrbl_base._base._rpc_map import (
    _coerce_payload,
    _serialize_output,
    _validate_input,
)
from ...mapping import engine_resolver as _resolver
from tigrbl_runtime.runtime import executor as _executor

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/router/resource_proxy")


class _ResourceProxy:
    """Dynamic proxy that resolves operation payloads for core operations."""

    __slots__ = ("_model", "_serialize", "_router")

    def __init__(
        self, model: type, *, serialize: bool = True, router: Any = None
    ) -> None:  # pragma: no cover - trivial
        self._model = model
        self._serialize = serialize
        self._router = router

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<ResourceProxy {self._model.__name__}>"

    def __getattr__(self, alias: str) -> Callable[..., Awaitable[Any]]:
        logger.debug("Resolving core handler '%s' for %s", alias, self._model.__name__)
        handlers_root = getattr(self._model, "handlers", None)
        h_alias = getattr(handlers_root, alias, None) if handlers_root else None
        if h_alias is None or not hasattr(h_alias, "core"):
            logger.debug(
                "No core handler '%s' found for %s", alias, self._model.__name__
            )
            raise AttributeError(f"{self._model.__name__} has no core method '{alias}'")

        async def _call(
            payload: Any = None,
            *,
            db: Any | None = None,
            request: Any = None,
            ctx: Optional[Dict[str, Any]] = None,
        ) -> Any:
            raw_payload = _coerce_payload(payload)
            logger.debug(
                "Preparing %s.%s with payload %s",
                self._model.__name__,
                alias,
                raw_payload,
            )
            if alias == "bulk_delete" and not isinstance(raw_payload, Mapping):
                raw_payload = {"ids": raw_payload}
                logger.debug("Coerced bulk_delete payload to mapping: %s", raw_payload)
            norm_payload = _validate_input(self._model, alias, alias, raw_payload)

            seed_ctx: Dict[str, Any] = dict(ctx or {})

            release_db = None
            if db is None:
                db, release_db = _resolver.acquire(
                    router=self._router, model=self._model, op_alias=alias
                )

            seed_ctx.setdefault("payload", norm_payload)
            seed_ctx.setdefault("db", db)
            if request is not None:
                seed_ctx.setdefault("request", request)
            app_ref = (
                getattr(request, "app", None)
                or seed_ctx.get("app")
                or self._router
                or self._model
            )
            seed_ctx.setdefault("app", app_ref)
            seed_ctx.setdefault("router", seed_ctx.get("router") or app_ref)
            seed_ctx.setdefault("model", self._model)
            seed_ctx.setdefault("op", alias)
            seed_ctx.setdefault("method", alias)
            seed_ctx.setdefault("target", alias)

            try:
                if self._serialize:
                    seed_ctx["response_serializer"] = lambda result: _serialize_output(
                        self._model, alias, alias, result
                    )
                return await _executor.invoke_op(
                    request=request,
                    db=db,
                    model=self._model,
                    alias=alias,
                    ctx=seed_ctx,
                )
            finally:
                if release_db is not None:
                    try:
                        release_db()
                    except Exception:
                        logger.debug("Error releasing core proxy DB", exc_info=True)

        _call.__name__ = f"{self._model.__name__}.{alias}"
        _call.__qualname__ = _call.__name__
        _call.__doc__ = f"Helper for core call {self._model.__name__}.{alias}"
        return _call
