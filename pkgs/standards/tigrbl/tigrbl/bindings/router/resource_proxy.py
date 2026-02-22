from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict, Mapping, Optional

from ..rpc import _coerce_payload, _validate_input, _serialize_output
from ...transport.dispatch import dispatch_operation
from ...engine import resolver as _resolver

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/router/resource_proxy")


class _ResourceProxy:
    """Dynamic proxy that executes core operations."""

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
                "Calling %s.%s with payload %s",
                self._model.__name__,
                alias,
                raw_payload,
            )
            if alias == "bulk_delete" and not isinstance(raw_payload, Mapping):
                raw_payload = {"ids": raw_payload}
                logger.debug("Coerced bulk_delete payload to mapping: %s", raw_payload)
            norm_payload = _validate_input(self._model, alias, alias, raw_payload)
            logger.debug(
                "Validated payload for %s.%s: %s",
                self._model.__name__,
                alias,
                norm_payload,
            )

            seed_ctx: Dict[str, Any] = dict(ctx or {})
            serializer = (
                (lambda r: _serialize_output(self._model, alias, alias, r))
                if self._serialize
                else (lambda r: r)
            )

            # Acquire DB if one was not explicitly provided (op > model > api > app)
            _release_db = None
            if db is None:
                try:
                    logger.debug(
                        "Acquiring DB for %s.%s via resolver",
                        self._model.__name__,
                        alias,
                    )
                    db, _release_db = _resolver.acquire(
                        api=self._router, model=self._model, op_alias=alias
                    )
                except Exception:
                    logger.exception(
                        "DB acquire failed for %s.%s; no default configured?",
                        self._model.__name__,
                        alias,
                    )
                    raise
            else:
                logger.debug("Using provided DB for %s.%s", self._model.__name__, alias)

            try:
                return await dispatch_operation(
                    router=self._router,
                    request=request,
                    db=db,
                    model_or_name=self._model,
                    alias=alias,
                    target=alias,
                    payload=norm_payload,
                    seed_ctx=seed_ctx,
                    rpc_mode=True,
                    response_serializer=serializer,
                )
            finally:
                if _release_db is not None:
                    try:
                        _release_db()
                        logger.debug(
                            "Released DB for %s.%s", self._model.__name__, alias
                        )
                    except Exception:
                        logger.debug(
                            "Non-fatal: error releasing acquired DB session",
                            exc_info=True,
                        )

        _call.__name__ = f"{self._model.__name__}.{alias}"
        _call.__qualname__ = _call.__name__
        _call.__doc__ = f"Helper for core call {self._model.__name__}.{alias}"
        return _call
