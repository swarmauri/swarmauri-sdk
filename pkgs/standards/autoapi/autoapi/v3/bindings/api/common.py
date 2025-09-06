from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/api/common")


class AttrDict(dict):
    """Dictionary providing attribute-style access."""

    def __getattr__(self, item: str) -> Any:  # pragma: no cover - trivial
        try:
            return self[item]
        except KeyError as e:  # pragma: no cover - debug aid
            raise AttributeError(item) from e

    def __setattr__(self, key: str, value: Any) -> None:  # pragma: no cover - trivial
        self[key] = value


# Public type for the API facade object users pass to include_model(...)
ApiLike = Any


def _resource_name(model: type) -> str:
    """
    Compute the API resource segment.

    Policy:
      - Prefer explicit `__resource__` when present (caller-controlled).
      - Otherwise, use the model *class name* in lowercase.
      - DO NOT use `__tablename__` here (strictly DB-only per project policy).
    """
    return getattr(model, "__resource__", model.__name__.lower())


def _default_prefix(model: type) -> str:
    """Default mount prefix for a model router.

    Historically routers were mounted under ``/{resource}``, resulting in
    duplicated path segments such as ``/item/item``.  To expose REST endpoints
    under ``/item`` we now mount routers at the application root by default.
    """
    return ""


def _has_include_router(obj: Any) -> bool:
    return hasattr(obj, "include_router") and callable(getattr(obj, "include_router"))


def _mount_router(app_or_router: Any, router: Any, *, prefix: str) -> None:
    """
    Best-effort mount onto a FastAPI app or Router.
    If not available, we still attach router under api.routers for later use.
    """
    if app_or_router is None:
        return
    try:
        if _has_include_router(app_or_router):
            app_or_router.include_router(router, prefix=prefix)  # FastAPI / Router
    except Exception:
        logger.exception("Failed to mount router at %s", prefix)


def _ensure_api_ns(api: ApiLike) -> None:
    """
    Ensure containers exist on the api facade object.
    """
    for attr, default in (
        ("models", {}),
        ("tables", AttrDict()),
        ("schemas", SimpleNamespace()),
        ("handlers", SimpleNamespace()),
        ("hooks", SimpleNamespace()),
        ("rpc", SimpleNamespace()),
        ("rest", SimpleNamespace()),
        ("routers", {}),
        ("columns", {}),
        ("table_config", {}),
        ("core", SimpleNamespace()),  # helper method proxies
        ("core_raw", SimpleNamespace()),
    ):
        if not hasattr(api, attr):
            setattr(api, attr, default)
