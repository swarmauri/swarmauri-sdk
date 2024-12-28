# importer.py

import sys
import importlib
import logging
from importlib.machinery import ModuleSpec
from types import ModuleType

from .plugin_manager import (
    get_entry_points,
    process_plugin,
    PluginLoadError,
    PluginValidationError
)
from .registry import get_external_module_path
from .interface_registry import INTERFACE_REGISTRY

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SwarmauriImporter:
    """
    Responsible for dynamically importing plugins and managing the swarmauri namespace.
    """
    def __init__(self):
        # Use INTERFACE_REGISTRY keys to define valid namespaces
        self.VALID_NAMESPACES = set(INTERFACE_REGISTRY.keys())

    def find_spec(self, fullname, path=None, target=None):
        """
        Locate the module spec for the requested fullname.

        :param fullname: Full module name (e.g., 'swarmauri.chunkers.NotRealChunker').
        :param path: Optional path for finding the module.
        :param target: Unused.
        :return: ModuleSpec or None if not found.
        """
        logger.debug(f"find_spec called for: {fullname}")

        # Only handle 'swarmauri' or 'swarmauri.*'
        if fullname == "swarmauri" or fullname.startswith("swarmauri."):
            namespace_parts = fullname.split(".")
            parent = ".".join(namespace_parts[:2])  # e.g. 'swarmauri.chunkers'

            # If parent is a valid namespace, create placeholder if needed
            if parent and parent not in sys.modules and parent in self.VALID_NAMESPACES:
                logger.debug(f"Creating placeholder for parent namespace: {parent}")
                spec = ModuleSpec(parent, self)
                spec.submodule_search_locations = []
                return spec

            # Check for an external module mapping
            external_module_path = get_external_module_path(fullname)
            if external_module_path:
                logger.debug(f"Mapping found: {fullname} -> {external_module_path}")
                return ModuleSpec(fullname, self)

            # Attempt to discover and register the plugin dynamically
            if self._try_register_plugin(fullname):
                logger.debug(f"Plugin discovered: {fullname}")
                external_module_path = get_external_module_path(fullname)
                if external_module_path:
                    logger.debug(f"Mapping found after registration: {fullname} -> {external_module_path}")
                    return ModuleSpec(fullname, self)

            logger.debug(f"Module '{fullname}' not found. Returning None.")
            return None

        # Not in 'swarmauri' namespace
        logger.debug(f"Module '{fullname}' is not in the 'swarmauri' namespace.")
        return None

    def _try_register_plugin(self, fullname):
        """
        Attempt to register a plugin dynamically using the plugin manager.
        Returns True if the plugin was successfully registered, False otherwise.
        """
        try:
            namespace, _, plugin_name = fullname.rpartition(".")
            if not namespace.startswith("swarmauri."):
                return False

            # Extract the local namespace (e.g., 'toolkits' from 'swarmauri.toolkits')
            local_namespace = namespace[len("swarmauri."):]
            grouped_entry_points = get_entry_points()  # This is now cached
            logger.debug(f"Grouped entry points: {grouped_entry_points}")
            entry_points = grouped_entry_points.get(local_namespace, [])
            logger.debug(f"Potential entry points for '{local_namespace}': {entry_points}")

            for entry_point in entry_points:
                if entry_point.name == plugin_name:
                    # Process (load/validate/register) the plugin
                    process_plugin(entry_point)
                    # If successful, the plugin is in sys.modules at this point
                    logger.debug(f"Successfully processed plugin '{fullname}'")
                    return True

        except PluginLoadError as e:
            # Plugin import or load issues
            logger.error(f"Could not load plugin '{fullname}': {e}")
        except PluginValidationError as e:
            # Plugin validation issues
            logger.error(f"Validation failed for plugin '{fullname}': {e}")
        except Exception as e:
            # Catch-all for anything unexpected
            logger.exception(f"Unexpected error registering plugin '{fullname}': {e}")

        return False

    def create_module(self, spec):
        """
        Create a module instance. For namespace modules, create a new ModuleType.

        :param spec: ModuleSpec containing metadata for the module.
        :return: The created or imported module.
        """
        logger.debug(f"create_module called for: {spec.name}")

        # Check if the module is already in sys.modules
        if spec.name in sys.modules:
            logger.debug(f"Module '{spec.name}' already in sys.modules. Returning cached module.")
            return sys.modules[spec.name]

        # Handle modules mapped to an external path
        external_module_path = get_external_module_path(spec.name)
        if external_module_path:
            logger.debug(f"Importing external module '{spec.name}' from '{external_module_path}'.")
            module = importlib.import_module(external_module_path)
            sys.modules[spec.name] = module
            return module

        # Handle namespace modules
        if spec.submodule_search_locations is not None:
            logger.debug(f"Creating namespace module for '{spec.name}'.")
            module = ModuleType(spec.name)
            module.__path__ = spec.submodule_search_locations
            sys.modules[spec.name] = module
            return module

        logger.error(f"Cannot create module '{spec.name}'. Raising ImportError.")
        raise ImportError(f"Cannot create module {spec.name}")

    def exec_module(self, module):
        """
        Execute the module. Typically no-op for namespace modules.
        """
        if hasattr(module, "__path__"):
            logger.debug(f"Executing namespace module: {module.__name__}")
        else:
            logger.debug(f"Executing regular module: {module.__name__}")


# Add the importer to sys.meta_path if not already present
if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
    sys.meta_path.insert(0, SwarmauriImporter())
