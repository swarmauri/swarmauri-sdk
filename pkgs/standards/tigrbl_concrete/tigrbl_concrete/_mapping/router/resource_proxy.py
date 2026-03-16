from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional


class _ResourceProxy:
    """Lightweight proxy over model handler cores."""

    __slots__ = ("_model", "_serialize", "_router")

    def __init__(
        self, model: type, *, serialize: bool = True, router: Any = None
    ) -> None:
        self._model = model
        self._serialize = serialize
        self._router = router

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
            core = getattr(h_alias, "core")
            result = await core(payload, db=db, request=request, ctx=dict(ctx or {}))
            return result

        _call.__name__ = f"{self._model.__name__}.{alias}"
        _call.__qualname__ = _call.__name__
        _call.__doc__ = f"Helper for core call {self._model.__name__}.{alias}"
        return _call
