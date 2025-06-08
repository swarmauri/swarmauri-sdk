import sys as _sys
from .logging_utils import get_logger
from .importer import SwarmauriImporter
from .plugin_manager import discover_and_register_plugins

logger = get_logger(__name__)

try:
    if not any(isinstance(importer, SwarmauriImporter) for importer in _sys.meta_path):
        logger.swarmauri("Registering SwarmauriImporter in _sys.meta_path.")
        _sys.meta_path.insert(0, SwarmauriImporter())
    else:
        logger.swarmauri("SwarmauriImporter is already registered.")
except Exception as e:
    logger.error(f"Failed to register SwarmauriImporter: {e}")
    raise

try:
    discover_and_register_plugins()
except Exception as e:
    logger.error(f"Failed to discover/register plugins: {e}")
    raise
