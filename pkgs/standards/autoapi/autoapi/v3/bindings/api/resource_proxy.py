from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Awaitable, Callable, Dict, Mapping, Optional

from ..rpc import (
    _coerce_payload,
    _get_phase_chains,
    _validate_input,
    _serialize_output,
)
from ...runtime import executor as _executor
from ...engine import resolver as _resolver
from ...column.collect import collect_columns

logger = logging.getLogger(__name__)


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
        handlers_root = getattr(self._model, "handlers", None)
        h_alias = getattr(handlers_root, alias, None) if handlers_root else None
        if h_alias is None or not hasattr(h_alias, "core"):
            raise AttributeError(f"{self._model.__name__} has no core method '{alias}'")

        async def _call(
            payload: Any = None,
            *,
            db: Any | None = None,
            request: Any = None,
            ctx: Optional[Dict[str, Any]] = None,
        ) -> Any:
            raw_payload = _coerce_payload(payload)
            if alias == "bulk_delete" and not isinstance(raw_payload, Mapping):
                raw_payload = {"ids": raw_payload}
            norm_payload = _validate_input(self._model, alias, alias, raw_payload)

            base_ctx: Dict[str, Any] = dict(ctx or {})
            base_ctx.setdefault("payload", norm_payload)
            base_ctx.setdefault("specs", collect_columns(self._model))
            temp_ctx = SimpleNamespace(temp={})
            specs = base_ctx["specs"]
            payload = base_ctx["payload"]
            for field, spec in specs.items():
                paired = getattr(getattr(spec, "io", None), "_paired", None)
                if paired and field not in payload:
                    raw = paired.gen(temp_ctx)
                    payload[field] = paired.store(raw, temp_ctx)
                    base_ctx.setdefault("response_extras", {})[paired.alias] = raw
            if request is not None:
                base_ctx.setdefault("request", request)
            base_ctx.setdefault(
                "env",
                SimpleNamespace(
                    method=alias, params=norm_payload, target=alias, model=self._model
                ),
            )
            if self._serialize:
                base_ctx.setdefault(
                    "response_serializer",
                    lambda r: _serialize_output(self._model, alias, alias, r),
                )
            else:
                base_ctx.setdefault("response_serializer", lambda r: r)

            # Acquire DB if one was not explicitly provided (op > model > api > app)
            _release_db = None
            if db is None:
                try:
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

            base_ctx.setdefault("db", db)
            phases = _get_phase_chains(self._model, alias)
            try:
                result = await _executor._invoke(
                    request=request,
                    db=db,
                    phases=phases,
                    ctx=base_ctx,
                )
                extras = base_ctx.get("response_extras") or {}
                if isinstance(result, dict) and extras:
                    result = {**result, **extras}
                return result
            finally:
                if _release_db is not None:
                    try:
                        _release_db()
                    except Exception:
                        logger.debug(
                            "Non-fatal: error releasing acquired DB session",
                            exc_info=True,
                        )

        _call.__name__ = f"{self._model.__name__}.{alias}"
        _call.__qualname__ = _call.__name__
        _call.__doc__ = f"Helper for core call {self._model.__name__}.{alias}"
        return _call
