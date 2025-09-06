# autoapi/v3/bindings/handlers/namespaces.py
from __future__ import annotations
import logging

from types import SimpleNamespace

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/handlers/namespaces")


def _ensure_alias_hooks_ns(model: type, alias: str) -> SimpleNamespace:
    hooks_root = getattr(model, "hooks", None)
    if hooks_root is None:
        hooks_root = SimpleNamespace()
        setattr(model, "hooks", hooks_root)

    ns = getattr(hooks_root, alias, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(hooks_root, alias, ns)

    if not hasattr(ns, "HANDLER"):
        setattr(ns, "HANDLER", [])
    return ns


def _ensure_alias_handlers_ns(model: type, alias: str) -> SimpleNamespace:
    handlers_root = getattr(model, "handlers", None)
    if handlers_root is None:
        handlers_root = SimpleNamespace()
        setattr(model, "handlers", handlers_root)

    ns = getattr(handlers_root, alias, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(handlers_root, alias, ns)

    hooks_ns = _ensure_alias_hooks_ns(model, alias)
    if not hasattr(ns, "HANDLER"):
        setattr(ns, "HANDLER", getattr(hooks_ns, "HANDLER"))
    return ns


__all__ = ["_ensure_alias_hooks_ns", "_ensure_alias_handlers_ns"]
