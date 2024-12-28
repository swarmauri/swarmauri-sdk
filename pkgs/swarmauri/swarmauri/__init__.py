# swarmauri/__init__.py
# pkg_resources-style namespace
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    pass

import sys
import logging
from .importer import SwarmauriImporter
from .plugin_manager import discover_and_register_plugins

logger = logging.getLogger(__name__)

try:
    if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
        logger.info("Registering SwarmauriImporter in sys.meta_path.")
        sys.meta_path.insert(0, SwarmauriImporter())
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
