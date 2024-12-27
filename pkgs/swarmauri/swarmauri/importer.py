# importer.py

import sys
import importlib
import logging
from importlib.machinery import ModuleSpec
from types import ModuleType
from .plugin_manager import get_entry_points, validate_and_register_plugin
from .registry import get_external_module_path

logger = logging.getLogger(__name__)


class SwarmauriImporter:
    """
    Responsible for dynamically importing plugins and managing the swarmauri namespace.
    """

    def find_spec(self, fullname, path, target=None):
        """
        Locate the module spec for the requested fullname.

        :param fullname: Full module name to locate (e.g., 'swarmauri.toolkits.MyPlugin').
        :return: ModuleSpec or None if not found.
        """
        logger.debug(f"find_spec called for: {fullname}")

        # Check if the fullname is part of the swarmauri namespace
        if fullname.startswith("swarmauri"):
            external_module_path = get_external_module_path(fullname)
            if external_module_path:
                logger.debug(f"Mapping found: {fullname} -> {external_module_path}")
                return ModuleSpec(fullname, self)

            # Attempt to discover and register the plugin dynamically
            if self._try_register_plugin(fullname):
                external_module_path = get_external_module_path(fullname)
                if external_module_path:
                    return ModuleSpec(fullname, self)

            # Handle namespace modules
            parent, _, _ = fullname.rpartition(".")
            if parent and parent not in sys.modules:
                logger.debug(f"Parent module '{parent}' not found. Cannot create namespace module: {fullname}")
                return None

            logger.debug(f"Creating placeholder for namespace module: {fullname}")
            spec = ModuleSpec(fullname, self)
            spec.submodule_search_locations = []
            return spec

        logger.debug(f"Module '{fullname}' is not in the 'swarmauri.' namespace.")
        return None

    def _try_register_plugin(self, fullname):
        """
        Attempt to register a plugin dynamically using the plugin manager.

        :param fullname: Full namespace path of the plugin (e.g., 'swarmauri.toolkits.MyPlugin').
        :return: True if the plugin was successfully registered, False otherwise.
        """
        try:
            namespace, _, plugin_name = fullname.rpartition(".")
            if not namespace.startswith("swarmauri."):
                return False

            # Extract the local namespace within swarmauri (e.g., 'toolkits' from 'swarmauri.toolkits')
            local_namespace = namespace[len("swarmauri."):]

            # Fetch and filter entry points dynamically
            grouped_entry_points = get_entry_points()
            entry_points = grouped_entry_points.get(local_namespace, [])
            for entry_point in entry_points:
                if entry_point.name == plugin_name:
                    # Validate and register the plugin
                    plugin_class = entry_point.load()
                    validate_and_register_plugin(entry_point, plugin_class, None)
                    sys.modules[fullname] = plugin_class
                    logger.info(f"Successfully registered and loaded plugin '{fullname}'")
                    return True

        except Exception as e:
            logger.error(f"Failed to register plugin '{fullname}': {e}")
            return False

    def create_module(self, spec):
        """
        Create a namespace module or dynamically import an existing module.

        :param spec: ModuleSpec object containing module metadata.
        :return: The created or imported module.
        """
        if spec.name in sys.modules:
            return sys.modules[spec.name]

        if spec.submodule_search_locations is not None:
            logger.debug(f"Creating namespace module for: {spec.name}")
            module = ModuleType(spec.name)
            module.__path__ = spec.submodule_search_locations
            sys.modules[spec.name] = module
            return module

        external_module_path = get_external_module_path(spec.name)
        if external_module_path:
            logger.debug(f"Dynamically importing: {spec.name} -> {external_module_path}")
            module = importlib.import_module(external_module_path)
            sys.modules[spec.name] = module
            return module

        return None

    def exec_module(self, module):
        """
        Execute the module. For namespace modules, no additional logic is needed.

        :param module: The module object to execute.
        """
        if hasattr(module, "__path__"):
            logger.debug(f"Executing namespace module: {module.__name__}")
        else:
            logger.debug(f"Executing regular module: {module.__name__}")


# Add the importer to sys.meta_path
if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
    sys.meta_path.insert(0, SwarmauriImporter())
