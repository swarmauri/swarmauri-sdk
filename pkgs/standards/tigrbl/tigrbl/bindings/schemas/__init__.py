# tigrbl/v3/bindings/schemas/__init__.py
from __future__ import annotations
import logging

from .builder import build_and_attach

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/schemas/__init__")

__all__ = ["build_and_attach"]
