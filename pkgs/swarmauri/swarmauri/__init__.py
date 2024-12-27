# Namespace package setup
import sys
import os
import logging
from .importer import SwarmauriImporter
from .plugin_manager import discover_and_register_plugins

# Set up logging
logger = logging.getLogger(__name__)

# Ensure the SwarmauriImporter is registered in sys.meta_path
try:
    if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
        logger.info("Registering SwarmauriImporter in sys.meta_path.")
        sys.meta_path.insert(0, SwarmauriImporter())
    else:
        logger.info("SwarmauriImporter is already registered.")
except Exception as e:
    logger.error(f"Failed to register SwarmauriImporter: {e}")
    raise

# Optionally discover and register plugins on initialization
# try:
#     discovery_flag = os.getenv("ENABLE_PLUGIN_DISCOVERY", "true").lower()
#     if discovery_flag not in {"true", "false"}:
#         logger.warning(f"Unexpected value for ENABLE_PLUGIN_DISCOVERY: {discovery_flag}. Defaulting to 'true'.")
#         discovery_flag = "true"

#     if discovery_flag == "true":
#         logger.info("Discovering and registering plugins...")
#         discover_and_register_plugins()
#         logger.info("Plugin discovery and registration completed.")
#     else:
#         logger.info("Plugin discovery is disabled by ENABLE_PLUGIN_DISCOVERY flag.")

# except Exception as e:
#     logger.error(f"Failed to discover and register plugins: {e}")
#     raise