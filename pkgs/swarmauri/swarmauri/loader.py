import importlib
import sys

def load_component(component_name):
    try:
        module = importlib.import_module(component_name)
        return module
    except ModuleNotFoundError:
        print(f"Component '{component_name}' not found.")
        sys.exit(1)
