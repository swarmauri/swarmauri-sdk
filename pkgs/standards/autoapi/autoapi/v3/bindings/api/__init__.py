from __future__ import annotations
import logging

from .common import AttrDict, _default_prefix, _mount_router  # noqa: F401
from .include import include_model, include_models, _seed_security_and_deps  # noqa: F401
from .rpc import rpc_call

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/api/__init__")

__all__ = ["include_model", "include_models", "rpc_call"]
