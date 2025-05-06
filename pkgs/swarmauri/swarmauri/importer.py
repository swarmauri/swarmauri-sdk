# importer.py

import sys
import importlib
import logging
from importlib.machinery import ModuleSpec
from types import ModuleType

from .plugin_citizenship_registry import PluginCitizenshipRegistry
from .interface_registry import InterfaceRegistry

logger = logging.getLogger(__name__)


class SwarmauriImporter:
    """
    Custom importer for the 'swarmauri' namespace.
    Handles dynamic loading of plugins based on the registries.
    """

    def __init__(self):
        # Define valid namespaces based on interface registry
        self.VALID_NAMESPACES = set(InterfaceRegistry.INTERFACE_REGISTRY.keys())

    def find_spec(self, fullname, path=None, target=None):
        logger.debug(f"find_spec called for: {fullname}")

        if fullname == "swarmauri" or fullname.startswith("swarmauri."):
            # Handle parent namespaces
            namespace_parts = fullname.split(".")
            if (
                len(namespace_parts) == 2
                and fullname not in sys.modules
                and fullname in self.VALID_NAMESPACES
            ):
                logger.debug(f"Creating placeholder for parent namespace: {fullname}")
                spec = ModuleSpec(fullname, self)
                spec.submodule_search_locations = []
                return spec

            # Check PluginCitizenshipRegistry.total_registry() for mappings
            external_module_path = PluginCitizenshipRegistry.get_external_module_path(
                fullname
            )
            if external_module_path:
                logger.debug(
                    f"Found external module mapping: {fullname} -> {external_module_path}"
                )
                return ModuleSpec(fullname, self)

            # If lazy, then we need to add LazyLoader
            external_module_path = PluginCitizenshipRegistry.get_external_module_path(
                fullname
            )
            if external_module_path:
                # If we detect lazy strategy, then we utilize LazyLoader
                logger.debug(
                    f"Found external module mapping: {fullname} -> {external_module_path}"
                )
                return ModuleSpec(fullname, importlib.util.LazyLoader(self))

            logger.debug(f"Module '{fullname}' not found. Returning None.")
            return None

        logger.debug(f"Module '{fullname}' is not in 'swarmauri' namespace.")
        return None

    def create_module(self, spec):
        logger.debug(f"create_module called for: {spec.name}")

        if spec.name in sys.modules:
            logger.debug(
                f"Module '{spec.name}' already in sys.modules. Returning cached module."
            )
            return sys.modules[spec.name]

        external_module_path = PluginCitizenshipRegistry.get_external_module_path(
            spec.name
        )
        if external_module_path:
            logger.debug(
                f"Importing external module '{spec.name}' from '{external_module_path}'"
            )
            module = importlib.import_module(external_module_path)
            sys.modules[spec.name] = module
            return module

        if spec.submodule_search_locations is not None:
            logger.debug(f"Creating namespace module '{spec.name}'.")
            module = ModuleType(spec.name)
            module.__path__ = spec.submodule_search_locations
            sys.modules[spec.name] = module
            return module

        logger.error(f"Cannot create module '{spec.name}'. Raising ImportError.")
        raise ImportError(f"Cannot create module {spec.name}")

    def exec_module(self, module):
        if hasattr(module, "__path__"):
            logger.debug(f"Executing namespace module: {module.__name__}")
        else:
            logger.debug(f"Executing regular module: {module.__name__}")


# Register the custom importer
if not any(isinstance(imp, SwarmauriImporter) for imp in sys.meta_path):
    logger.info("Registering SwarmauriImporter in sys.meta_path.")
    sys.meta_path.insert(0, SwarmauriImporter())
else:
    logger.info("SwarmauriImporter is already registered.")
