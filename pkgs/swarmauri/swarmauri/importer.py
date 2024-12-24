import sys
import importlib
from .registry import get_external_module_path

class SwarmauriImporter:
    def find_spec(self, fullname, path, target=None):
        """
        Intercept import attempts under the 'swarmauri' namespace.
        
        :param fullname: Full module name being imported (e.g., "swarmauri.llms.OpenAIModel.OpenAiModel").
        :param path: The path of the module (not used here).
        :param target: Target module (not used here).
        :return: None if the module is not managed by this importer.
        """
        # Check if the resource path exists in the registry
        external_module_path = get_external_module_path(fullname)
        if external_module_path:
            # Dynamically load the external module
            module = importlib.import_module(external_module_path)
            sys.modules[fullname] = module
            return module.__spec__
        return None

# Add the importer to sys.meta_path
sys.meta_path.insert(0, SwarmauriImporter())
