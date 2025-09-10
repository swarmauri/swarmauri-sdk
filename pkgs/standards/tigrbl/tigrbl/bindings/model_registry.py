# tigrbl/v3/bindings/model_registry.py
"""Registry helpers for model bindings."""

from __future__ import annotations

import logging
from typing import Set

from ..config.constants import TIGRBL_REGISTRY_LISTENER_ATTR
from ..op import OpspecRegistry, get_registry

from .model_helpers import _Key

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/model_registry")


def _ensure_registry_listener(model: type) -> None:
    """
    Subscribe (once) to the per-model OpspecRegistry so future register_ops/add/remove/set
    calls automatically refresh the model namespaces.
    """

    reg: OpspecRegistry = get_registry(model)

    # If we already subscribed, skip
    if getattr(model, TIGRBL_REGISTRY_LISTENER_ATTR, None):
        return

    def _on_registry_change(registry: OpspecRegistry, changed: Set[_Key]) -> None:
        from .model import rebind

        try:
            rebind(model, changed_keys=changed)  # targeted rebind
        except Exception as e:  # pragma: no cover
            logger.exception(
                "tigrbl: rebind failed for %s on ops %s: %s",
                model.__name__,
                changed,
                e,
            )

    reg.subscribe(_on_registry_change)
    # Keep a reference to avoid GC of the closure and to prevent double-subscribe
    setattr(model, TIGRBL_REGISTRY_LISTENER_ATTR, _on_registry_change)


def _ensure_op_ctx_attach_hook(model: type) -> None:
    """Patch the model's metaclass to auto-rebind on ctx-only op attachment."""

    meta = type(model)
    if getattr(meta, "__tigrbl_op_ctx_meta_patch__", False):
        return

    orig_meta_setattr = meta.__setattr__

    def _meta_setattr(cls, name, value):
        from .model import rebind
        from ..op.mro_collect import mro_collect_decorated_ops

        orig_meta_setattr(cls, name, value)
        fn = getattr(value, "__func__", value)
        decl = getattr(fn, "__tigrbl_op_decl__", None)
        if decl and getattr(cls, "__tigrbl_op_ctx_watch__", False):
            alias = decl.alias or name
            target = decl.target or "custom"
            mro_collect_decorated_ops.cache_clear()
            rebind(cls, changed_keys={(alias, target)})

    meta.__setattr__ = _meta_setattr  # type: ignore[attr-defined]
    setattr(meta, "__tigrbl_op_ctx_meta_patch__", True)


__all__ = [
    "_ensure_registry_listener",
    "_ensure_op_ctx_attach_hook",
]
