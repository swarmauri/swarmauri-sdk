from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Awaitable, Callable, Dict, Mapping, Optional

from ..rpc import _coerce_payload, _get_phase_chains, _validate_input, _serialize_output
from ...runtime import executor as _executor
from ...engine import resolver as _resolver

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/api/resource_proxy")


class _ResourceProxy:
    """Dynamic proxy that executes core operations."""

    __slots__ = ("_model", "_serialize", "_api")

    def __init__(
        self, model: type, *, serialize: bool = True, api: Any = None
    ) -> None:  # pragma: no cover - trivial
        self._model = model
        self._serialize = serialize
        self._api = api

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

            base_ctx: Dict[str, Any] = dict(ctx or {})
            base_ctx.setdefault("payload", norm_payload)
            if request is not None:
                logger.debug("Request provided for %s.%s", self._model.__name__, alias)
                base_ctx.setdefault("request", request)
            # surface contextual metadata for runtime atoms
            app_ref = getattr(request, "app", None) or base_ctx.get("app") or self._api
            base_ctx.setdefault("app", app_ref)
            base_ctx.setdefault("api", base_ctx.get("api") or self._api or app_ref)
            base_ctx.setdefault("model", self._model)
            base_ctx.setdefault("op", alias)
            base_ctx.setdefault("method", alias)
            base_ctx.setdefault("target", alias)
            base_ctx.setdefault(
                "env",
                SimpleNamespace(
                    method=alias, params=norm_payload, target=alias, model=self._model
                ),
            )
            if self._serialize:
                logger.debug(
                    "Serialization enabled for %s.%s", self._model.__name__, alias
                )
                base_ctx.setdefault(
                    "response_serializer",
                    lambda r: _serialize_output(self._model, alias, alias, r),
                )
            else:
                logger.debug(
                    "Serialization disabled for %s.%s", self._model.__name__, alias
                )
                base_ctx.setdefault("response_serializer", lambda r: r)

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
                        api=self._api, model=self._model, op_alias=alias
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

            base_ctx.setdefault("db", db)
            phases = _get_phase_chains(self._model, alias)
            logger.debug(
                "Executing phases %s for %s.%s", phases, self._model.__name__, alias
            )
            try:
                return await _executor._invoke(
                    request=request,
                    db=db,
                    phases=phases,
                    ctx=base_ctx,
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
