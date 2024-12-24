import sys
import importlib
import logging
from importlib.machinery import ModuleSpec
from types import ModuleType
from .registry import get_external_module_path, REGISTRY

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SwarmauriImporter:
    def find_spec(self, fullname, path, target=None):
        """
        Intercept import attempts under the 'swarmauri' namespace.
        """
        logger.debug(f"find_spec called for: {fullname}")
        
        # Check if the module exists in the registry
        external_module_path = get_external_module_path(fullname)
        if external_module_path:
            logger.debug(f"Mapping found: {fullname} -> {external_module_path}")
            return ModuleSpec(fullname, self)
        
        # Handle namespace modules
        if fullname.startswith("swarmauri"):
            # Ensure parent module is valid (e.g., "swarmauri.llms" exists)
            parent, _, _ = fullname.rpartition(".")
            if parent and parent not in sys.modules:
                logger.debug(f"Parent module '{parent}' not found. Cannot create namespace module: {fullname}")
                return None
            
            # Check if the module is an expected namespace component
            if fullname not in REGISTRY and fullname.count(".") > 1:
                logger.debug(f"Invalid namespace module: {fullname}")
                return None

            logger.debug(f"Creating placeholder for namespace module: {fullname}")
            spec = ModuleSpec(fullname, self)
            spec.submodule_search_locations = []  # Mark as a namespace
            return spec
        
        # If not a valid namespace or in the registry, return None
        logger.debug(f"Module '{fullname}' not found in registry or as a namespace module.")
        return None

    def create_module(self, spec):
        """
        Create a module instance. For namespace modules, create a new ModuleType.
        """
        if spec.name in sys.modules:
            return sys.modules[spec.name]

        # Handle namespace components
        if spec.submodule_search_locations is not None:
            logger.debug(f"Creating namespace module for: {spec.name}")
            module = ModuleType(spec.name)
            module.__path__ = spec.submodule_search_locations
            sys.modules[spec.name] = module
            return module

        # Handle external modules
        external_module_path = get_external_module_path(spec.name)
        if external_module_path:
            logger.debug(f"Dynamically importing: {spec.name} -> {external_module_path}")
            module = importlib.import_module(external_module_path)
            sys.modules[spec.name] = module
            return module

        return None

    def exec_module(self, module):
        """
        Execute the module. For namespace modules, this is a no-op.
        """
        if hasattr(module, "__path__"):
            logger.debug(f"Executing namespace module: {module.__name__}")
        else:
            logger.debug(f"Executing regular module: {module.__name__}")

# Add the importer to sys.meta_path
if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
    sys.meta_path.insert(0, SwarmauriImporter())
