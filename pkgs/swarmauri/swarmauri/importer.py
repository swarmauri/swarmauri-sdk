import sys
import importlib
from importlib.machinery import ModuleSpec
from .registry import get_external_module_path

class SwarmauriImporter:
    def find_spec(self, fullname, path, target=None):
        """
        Intercept import attempts under the 'swarmauri' namespace.
        
        :param fullname: Full module name being imported (e.g., "swarmauri.llms.OpenAIModel.OpenAiModel").
        :param path: The path of the module (not used here).
        :param target: Target module (not used here).
        :return: ModuleSpec if the module is managed by this importer, otherwise None.
        """
        # Check if the resource path exists in the registry
        external_module_path = get_external_module_path(fullname)
        if external_module_path:
            # Return a ModuleSpec for the dynamic import
            return ModuleSpec(fullname, self)
        return None

    def create_module(self, spec):
        """
        Dynamically load the external module.
        """
        external_module_path = get_external_module_path(spec.name)
        if external_module_path:
            module = importlib.import_module(external_module_path)
            sys.modules[spec.name] = module
            return module
        return None

# Add the importer to sys.meta_path
if not any(isinstance(importer, SwarmauriImporter) for importer in sys.meta_path):
    sys.meta_path.insert(0, SwarmauriImporter())
