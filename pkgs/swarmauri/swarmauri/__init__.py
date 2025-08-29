import sys as _sys
import logging
from .importer import SwarmauriImporter
from .plugin_manager import discover_and_register_plugins

logger = logging.getLogger(__name__)

try:
    if not any(isinstance(importer, SwarmauriImporter) for importer in _sys.meta_path):
        logger.info("Registering SwarmauriImporter in _sys.meta_path.")
        _sys.meta_path.insert(0, SwarmauriImporter())
    else:
        logger.info("SwarmauriImporter is already registered.")
except Exception as e:
    logger.error(f"Failed to register SwarmauriImporter: {e}")
    raise

try:
    discover_and_register_plugins()
except Exception as e:
    logger.error(f"Failed to discover/register plugins: {e}")
    raise
