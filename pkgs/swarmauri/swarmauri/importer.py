# importer.py
import sys
import importlib
import logging
from importlib.machinery import ModuleSpec
from types import ModuleType
from .plugin_manager import get_entry_points, process_plugin
from .registry import get_external_module_path
from .interface_registry import INTERFACE_REGISTRY

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SwarmauriImporter:
    """
    Responsible for dynamically importing plugins and managing the swarmauri namespace.
    """
    def __init__(self):
        # Use INTERFACE_REGISTRY keys directly to define valid namespaces
        self.VALID_NAMESPACES = set(INTERFACE_REGISTRY.keys())

    def find_spec(self, fullname, path=None, target=None):
        """
        Locate the module spec for the requested fullname.

        :param fullname: Full module name to locate (e.g., 'swarmauri.toolkits.MyPlugin').
        :param path: Optional path for finding the module.
        :param target: Target module (unused).
        :return: ModuleSpec or None if not found.
        """
        logger.debug(f"find_spec called for: {fullname}")

        if fullname == "swarmauri" or fullname.startswith("swarmauri."):
            namespace_parts = fullname.split(".")
            # Check if the module has an external mapping
            external_module_path = get_external_module_path(fullname)
            if external_module_path:
                logger.debug(f"Mapping found: {fullname} -> {external_module_path}")
                return ModuleSpec(fullname, self)

            # Attempt to discover and register the plugin dynamically
            if self._try_register_plugin(fullname):
                external_module_path = get_external_module_path(fullname)
                if external_module_path:
                    return ModuleSpec(fullname, self)

            # Handle namespace modules (e.g., "swarmauri.toolkits")
            parent, _, _ = fullname.rpartition(".")
            if parent and parent not in sys.modules:
                logger.debug(f"Parent module '{parent}' not found. Cannot create namespace module: {fullname}")
                return None

            # Create a placeholder for namespace module
            part = '.'.join(namespace_parts[:2])
            if part in self.VALID_NAMESPACES:
                logger.debug(f"Creating placeholder for namespace module: {part}")
                spec = ModuleSpec(part, self)
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
                    # Process the plugin via plugin manager
                    process_plugin(entry_point)
                    sys.modules[fullname] = entry_point.load()
                    logger.info(f"Successfully registered and loaded plugin '{fullname}'")
                    return True

        except Exception as e:
            logger.error(f"Failed to register plugin '{fullname}': {e}")
            return False

    def create_module(self, spec):
        if spec.name in sys.modules:
            return sys.modules[spec.name]

        external_module_path = get_external_module_path(spec.name)
        if external_module_path:
            module = importlib.import_module(external_module_path)
            sys.modules[spec.name] = module
            return module

        if spec.submodule_search_locations is not None:
            module = ModuleType(spec.name)
            module.__path__ = spec.submodule_search_locations
            sys.modules[spec.name] = module
            return module

        raise ImportError(f"Cannot create module {spec.name}")


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
