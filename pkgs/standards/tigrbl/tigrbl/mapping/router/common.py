from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/router/common")


class AttrDict(dict):
    """Dictionary providing attribute-style access."""

    @staticmethod
    def _is_internal_key(key: Any) -> bool:
        return isinstance(key, str) and key.startswith("__tigrbl_system_")

    def __iter__(self):  # pragma: no cover - container behavior
        for key in dict.__iter__(self):
            if not self._is_internal_key(key):
                yield key

    def keys(self):  # pragma: no cover - container behavior
        return tuple(iter(self))

    def items(self):  # pragma: no cover - container behavior
        return tuple((key, dict.__getitem__(self, key)) for key in self)

    def values(self):  # pragma: no cover - container behavior
        return tuple(dict.__getitem__(self, key) for key in self)

    def __len__(self) -> int:  # pragma: no cover - container behavior
        return sum(1 for _ in self.__iter__())

    def __getattr__(self, item: str) -> Any:  # pragma: no cover - trivial
        try:
            value = self[item]
        except KeyError as e:  # pragma: no cover - debug aid
            raise AttributeError(item) from e

        # Compatibility: table registries are model-centric (key access returns
        # the model class), but some call sites historically accessed
        # ``router.tables.ModelName.name`` expecting SQLAlchemy table metadata.
        # Attribute access preserves that by projecting mapped model classes to
        # their ``__table__`` object when available.
        if isinstance(value, type):
            table = getattr(value, "__table__", None)
            if table is not None:
                return table
        return value

    def __setattr__(self, key: str, value: Any) -> None:  # pragma: no cover - trivial
        self[key] = value


# Public type for the Router facade object users pass to include_table(...)
RouterLike = Any


def _default_prefix(model: type) -> str:
    """Default mount prefix for a model router.

    Historically routers were mounted under ``/{resource}``, resulting in
    duplicated path segments such as ``/item/item``.  To expose REST endpoints
    under ``/item`` we now mount routers at the application root by default.
    """
    logger.debug("Default prefix for %s is root '/'", model.__name__)
    return ""


def _has_include_router(obj: Any) -> bool:
    has_router = hasattr(obj, "include_router") and callable(
        getattr(obj, "include_router")
    )
    logger.debug("Object %s has include_router: %s", obj, has_router)
    return has_router


def _mount_router(app_or_router: Any, router: Any, *, prefix: str) -> None:
    """
    Best-effort mount onto a ASGI app or Router.
    If not available, we still attach router under router.routers for later use.
    """
    if app_or_router is None:
        logger.debug("No app/router; skipping mount for prefix %s", prefix)
        return
    try:
        if _has_include_router(app_or_router):
            logger.debug("Mounting router %s at prefix %s", router, prefix)
            app_or_router.include_router(router, prefix=prefix)  # ASGI / Router
        else:
            logger.debug(
                "Provided object %s lacks include_router; not mounting router",
                app_or_router,
            )
    except Exception:
        logger.exception("Failed to mount router at %s", prefix)


def _ensure_router_ns(router: RouterLike) -> None:
    """
    Ensure containers exist on the router facade object.
    """
    for attr, default in (
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
        if not hasattr(router, attr):
            setattr(router, attr, default)
            logger.debug("Initialized router.%s", attr)
        else:
            logger.debug("router already has attribute %s", attr)
