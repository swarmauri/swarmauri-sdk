import sys
import importlib
import logging
from importlib.machinery import ModuleSpec
from types import ModuleType
from .registry import get_external_module_path
from .plugin_manager import validate_and_register_plugin, get_entry_points

logger = logging.getLogger(__name__)


class SwarmauriImporter:
    """
    Responsible for dynamically importing plugins and managing the swarmauri namespace.
    """
    def find_spec(self, fullname, path, target=None):
        logger.debug(f"find_spec called for: {fullname}")

        # Handle swarmauri namespace
        if fullname.startswith("swarmauri"):
            external_module_path = get_external_module_path(fullname)
            if external_module_path:
                logger.debug(f"Mapping found: {fullname} -> {external_module_path}")
                return ModuleSpec(fullname, self)

            # Attempt to discover and register plugin
            if self._try_discover_plugin(fullname):
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

    def _try_discover_plugin(self, fullname):
        """
        Discover and register a plugin dynamically.

        :param fullname: Full namespace path of the plugin (e.g., 'swarmauri.agents.MyPlugin').
        :return: True if the plugin was successfully discovered and registered, False otherwise.
        """
        try:
            # Extract plugin name and resource kind
            resource_kind, _, plugin_name = fullname.rpartition(".")

            # Fetch all available entry points
            entry_points = get_entry_points()
            entry_point = next((ep for ep in entry_points if ep.name == plugin_name), None)
            if not entry_point:
                logger.error(f"No entry point found for plugin '{plugin_name}'.")
                return False

            # Delegate validation and registration to plugin_manager
            plugin_class = entry_point.load()
            validate_and_register_plugin(entry_point, plugin_class, None)
            return True

        except Exception as e:
            logger.error(f"Error during plugin discovery for '{fullname}': {e}")
            return False

    def create_module(self, spec):
        """
        Create a namespace module or dynamically import an existing module.
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
        """
        if hasattr(module, "__path__"):
            logger.debug(f"Executing namespace module: {module.__name__}")
        else:
            logger.debug(f"Executing regular module: {module.__name__}")


# Add the importer to sys.meta_path
if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
    sys.meta_path.insert(0, SwarmauriImporter())
