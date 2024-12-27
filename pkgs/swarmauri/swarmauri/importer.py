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

        :param fullname: Full module name to locate (e.g., 'swarmauri.chunkers.NotRealChunker').
        :param path: Optional path for finding the module.
        :param target: Target module (unused).
        :return: ModuleSpec or None if not found.
        """
        logger.debug(f"find_spec called for: {fullname}")

        if fullname == "swarmauri" or fullname.startswith("swarmauri."):
            namespace_parts = fullname.split(".")

            # Ensure parent namespace exists
            parent = '.'.join(namespace_parts[:2])  # Parent namespace (e.g., 'swarmauri.chunkers')
            if parent and parent not in sys.modules and parent in self.VALID_NAMESPACES:
                logger.debug(f"Creating placeholder for parent namespace: {parent}")
                spec = ModuleSpec(parent, self)
                spec.submodule_search_locations = []
                return spec

            # Check for external module mapping
            external_module_path = get_external_module_path(fullname)
            if external_module_path:
                logger.debug(f"Mapping found: {fullname} -> {external_module_path}")
                return ModuleSpec(fullname, self)

            # Attempt to discover and register the plugin dynamically
            if self._try_register_plugin(fullname):
                logger.debug(f"Attempting to discover module: {fullname}")
                external_module_path = get_external_module_path(fullname)
                if external_module_path:
                    logger.debug(f"Mapping found: {fullname} -> {external_module_path}")
                    return ModuleSpec(fullname, self)

            # If no mapping or valid plugin, ensure we do not create invalid placeholders
            logger.debug(f"Module '{fullname}' not found. Returning None.")
            return None

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
            logger.debug(f"Grouped entry points: '{grouped_entry_points}'")
            entry_points = grouped_entry_points.get(local_namespace, [])
            logger.debug(f"Entry points: '{entry_points}'")

            for entry_point in entry_points:
                if entry_point.name == plugin_name:
                    # Process the plugin via plugin manager
                    process_plugin(entry_point)
                    sys.modules[fullname] = entry_point.load()
                    logger.debug(f"Successfully registered and loaded plugin '{fullname}'")
                    return True

        except Exception as e:
            logger.error(f"Failed to register plugin '{fullname}': {e}")
            return False

    def create_module(self, spec):
        """
        Create a module instance. For namespace modules, create a new ModuleType.

        :param spec: ModuleSpec object containing metadata for the module.
        :return: The created or imported module.
        """
        logger.debug(f"create_module called for: {spec.name}")

        # Check if the module already exists in sys.modules
        if spec.name in sys.modules:
            logger.debug(f"Module '{spec.name}' already exists in sys.modules. Returning cached module.")
            return sys.modules[spec.name]

        # Handle modules mapped to an external path
        external_module_path = get_external_module_path(spec.name)
        if external_module_path:
            logger.debug(f"External module path found for '{spec.name}': {external_module_path}")
            module = importlib.import_module(external_module_path)
            sys.modules[spec.name] = module
            logger.debug(f"Successfully imported external module '{spec.name}' from '{external_module_path}'.")
            return module

        # Handle namespace modules
        if spec.submodule_search_locations is not None:
            logger.debug(f"Creating namespace module for '{spec.name}'.")
            module = ModuleType(spec.name)
            module.__path__ = spec.submodule_search_locations
            sys.modules[spec.name] = module
            logger.debug(f"Namespace module '{spec.name}' created with path: {spec.submodule_search_locations}.")
            return module

        # If no conditions match, raise an ImportError
        logger.error(f"Cannot create module '{spec.name}'. Raising ImportError.")
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
