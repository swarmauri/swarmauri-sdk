import sys
import importlib
from importlib.machinery import ModuleSpec
from .registry import get_external_module_path

class SwarmauriImporter:
    def find_spec(self, fullname, path, target=None):
        print(f"find_spec called for: {fullname}")
        external_module_path = get_external_module_path(fullname)
        if external_module_path:
            print(f"Mapping found: {fullname} -> {external_module_path}")
            return ModuleSpec(fullname, self)
        if fullname.startswith("swarmauri"):
            print(f"Creating placeholder for namespace module: {fullname}")
            return ModuleSpec(fullname, self)
        return None
        
    def create_module(self, spec):
        if spec.name in sys.modules:
            return sys.modules[spec.name]

        # Handle namespace components
        if not get_external_module_path(spec.name):
            print(f"Creating namespace module for: {spec.name}")
            module = ModuleType(spec.name)
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


# Add the importer to sys.meta_path
if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
    sys.meta_path.insert(0, SwarmauriImporter())
