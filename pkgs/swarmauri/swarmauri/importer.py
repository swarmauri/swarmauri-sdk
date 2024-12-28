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
        # Use the INTERFACE_REGISTRY keys to define valid namespaces
        self.VALID_NAMESPACES = set(INTERFACE_REGISTRY.keys())

    def find_spec(self, fullname, path=None, target=None):
        """
        Locate the module spec for the requested fullname.

        :param fullname: Full module name (e.g., 'swarmauri.chunkers.SentenceChunker').
        :param path: Optional path for finding the module.
        :param target: Unused by our importer.
        :return: ModuleSpec or None if not found.
        """
        logger.debug(f"find_spec called for: {fullname}")

        if fullname == "swarmauri" or fullname.startswith("swarmauri."):
            namespace_parts = fullname.split(".")
            parent = ".".join(namespace_parts[:2])  # e.g. 'swarmauri.chunkers'

            # If parent is a recognized namespace but not yet in sys.modules, create a placeholder
            if parent and parent not in sys.modules and parent in self.VALID_NAMESPACES:
                logger.debug(f"Creating placeholder for parent namespace: {parent}")
                spec = ModuleSpec(parent, self)
                spec.submodule_search_locations = []
                return spec

            # Check if it's already mapped to an external module
            external_module_path = get_external_module_path(fullname)
            if external_module_path:
                logger.debug(f"Found external module mapping: {fullname} -> {external_module_path}")
                return ModuleSpec(fullname, self)

            # Attempt to discover/register a plugin
            if self._try_register_plugin(fullname):
                # After registration, check again for an external mapping
                external_module_path = get_external_module_path(fullname)
                if external_module_path:
                    logger.debug(f"Mapping found after registration: {fullname} -> {external_module_path}")
                    return ModuleSpec(fullname, self)

            logger.debug(f"Module '{fullname}' not found. Returning None.")
            return None

        # Not part of the 'swarmauri' namespace
        logger.debug(f"Module '{fullname}' is not in 'swarmauri' namespace.")
        return None

    def _try_register_plugin(self, fullname):
        """
        Attempt to dynamically register a plugin by checking entry points.
        Returns True if the plugin was successfully discovered and registered,
        False otherwise.
        """
        try:
            namespace, _, plugin_name = fullname.rpartition(".")
            if not namespace.startswith("swarmauri."):
                return False

            local_namespace = namespace[len("swarmauri."):]  # e.g. 'chunkers'
            grouped_entry_points = get_entry_points()  # Uses cached entry points
            logger.debug(f"Grouped entry points: {grouped_entry_points}")

            entry_points = grouped_entry_points.get(local_namespace, [])
            for ep in entry_points:
                if ep.name == plugin_name:
                    process_plugin(ep)
                    logger.debug(f"Successfully processed plugin '{fullname}'.")
                    return True

        except PluginLoadError as e:
            logger.error(f"Could not load plugin '{fullname}': {e}")
        except PluginValidationError as e:
            logger.error(f"Validation failed for plugin '{fullname}': {e}")
        except Exception as e:
            logger.exception(f"Unexpected error registering plugin '{fullname}': {e}")

        return False

    def create_module(self, spec):
        """
        Create a module instance. For namespace modules, create a new ModuleType.
        For externally mapped modules, import the underlying Python module.
        """
        logger.debug(f"create_module called for: {spec.name}")

        if spec.name in sys.modules:
            logger.debug(f"Module '{spec.name}' already in sys.modules. Returning cached module.")
            return sys.modules[spec.name]

        # If there's a known external mapping, import it
        external_module_path = get_external_module_path(spec.name)
        if external_module_path:
            logger.debug(f"Importing external module '{spec.name}' from '{external_module_path}'")
            module = importlib.import_module(external_module_path)
            sys.modules[spec.name] = module
            return module

        # If it's a namespace module, create a blank module with submodule_search_locations
        if spec.submodule_search_locations is not None:
            logger.debug(f"Creating namespace module '{spec.name}'.")
            module = ModuleType(spec.name)
            module.__path__ = spec.submodule_search_locations
            sys.modules[spec.name] = module
            return module

        logger.error(f"Cannot create module '{spec.name}'. Raising ImportError.")
        raise ImportError(f"Cannot create module {spec.name}")

    def exec_module(self, module):
        """
        Execute the module. Typically a no-op for namespace modules.
        """
        if hasattr(module, "__path__"):
            logger.debug(f"Executing namespace module: {module.__name__}")
        else:
            logger.debug(f"Executing regular module: {module.__name__}")


# Register our custom importer if not already present
if not any(isinstance(imp, SwarmauriImporter) for imp in sys.meta_path):
    sys.meta_path.insert(0, SwarmauriImporter())
