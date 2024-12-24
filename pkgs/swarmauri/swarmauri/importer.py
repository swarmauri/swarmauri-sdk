import sys
import importlib
from importlib.machinery import ModuleSpec
from types import ModuleType
from .registry import get_external_module_path

class SwarmauriImporter:
    def find_spec(self, fullname, path, target=None):
        """
        Intercept import attempts under the 'swarmauri' namespace.
        """
        print(f"find_spec called for: {fullname}")
        
        # Check if the module exists in the registry
        external_module_path = get_external_module_path(fullname)
        if external_module_path:
            print(f"Mapping found: {fullname} -> {external_module_path}")
            return ModuleSpec(fullname, self)
        
        # Handle namespace modules
        if fullname.startswith("swarmauri"):
            print(f"Creating placeholder for namespace module: {fullname}")
            return ModuleSpec(fullname, self, is_namespace=True)
        
        return None

    def create_module(self, spec):
        """
        Create a module instance. For namespace modules, create a new ModuleType.
        """
        if spec.name in sys.modules:
            return sys.modules[spec.name]

        # Handle namespace components
        if spec.is_namespace:
            print(f"Creating namespace module for: {spec.name}")
            module = ModuleType(spec.name)
            module.__path__ = []  # Required for namespace packages
            sys.modules[spec.name] = module
            return module

        # Handle external modules
        external_module_path = get_external_module_path(spec.name)
        if external_module_path:
            print(f"Dynamically importing: {spec.name} -> {external_module_path}")
            module = importlib.import_module(external_module_path)
            sys.modules[spec.name] = module
            return module

        return None

    def exec_module(self, module):
        """
        Execute the module. For namespace modules, this is a no-op.
        """
        if hasattr(module, "__path__"):
            print(f"Executing namespace module: {module.__name__}")
        else:
            print(f"Executing regular module: {module.__name__}")

# Add the importer to sys.meta_path
if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
    sys.meta_path.insert(0, SwarmauriImporter())
