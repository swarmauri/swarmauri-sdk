import logging
from .attach import build_router_and_attach

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/__init__")

__all__ = ["build_router_and_attach"]
