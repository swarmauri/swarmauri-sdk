# swarmauri/__init__.py
from __future__ import annotations

import os
import logging
import sys as _sys

from .importer import SwarmauriImporter

logger = logging.getLogger(__name__)


def _register_importer_once() -> None:
    """
    Ensure SwarmauriImporter is present at the front of sys.meta_path exactly once.
    """
    try:
        if not any(isinstance(imp, SwarmauriImporter) for imp in _sys.meta_path):
            logger.info("Registering SwarmauriImporter in _sys.meta_path.")
            _sys.meta_path.insert(0, SwarmauriImporter())
        else:
            logger.info("SwarmauriImporter is already registered.")
    except Exception as e:
        logger.error("Failed to register SwarmauriImporter: %s", e)
        raise


def _env_flag(name: str, default: str = "0") -> bool:
    """
    Robust truthy env parsing: 1/true/yes/on (case-insensitive) => True.
    """
    val = os.environ.get(name, default)
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


def _auto_discover_if_enabled() -> None:
    """
    Auto-run plugin discovery unless explicitly disabled.
    When SWARMAURI_DISCOVERY_STATS is truthy, logs timing/counters.
    """
    if _env_flag("SWARMAURI_DISABLE_AUTO_DISCOVERY", default="0"):
        logger.debug("Auto discovery disabled via SWARMAURI_DISABLE_AUTO_DISCOVERY.")
        return

    try:
        # Local import keeps import graph minimal when discovery is disabled.
        from .plugin_manager import discover_and_register_plugins

        if _env_flag("SWARMAURI_DISCOVERY_STATS", default="0"):
            stats = discover_and_register_plugins(collect_stats=True) or {}
            logger.info(
                "Swarmauri discovery: groups=%s processed=%s ok=%s failed=%s "
                "fetch=%.4fs process=%.4fs",
                stats.get("groups"),
                stats.get("processed", 0),
                stats.get("succeeded", 0),
                stats.get("failed", 0),
                stats.get("fetch_seconds", 0.0),
                stats.get("process_seconds", 0.0),
            )
        else:
            discover_and_register_plugins()
    except Exception as e:
        logger.error("Failed to discover/register plugins: %s", e)
        raise


# Perform importer registration and (optionally) auto-discovery at import time.
_register_importer_once()
_auto_discover_if_enabled()

# Public API surface (intentionally minimal in __init__)
__all__ = ()
