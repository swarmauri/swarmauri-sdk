import importlib
import re


def get_classes_from_module(module_name: str):
    """
    Dynamically imports a module and retrieves a dictionary of class names and their corresponding class objects.

    :param module_name: The name of the module (e.g., "parsers", "agent").
    :return: A dictionary with class names as keys and class objects as values.
    """
    # Convert module name to lowercase to ensure consistency
    module_name_lower = module_name.lower()

    # Construct the full module path dynamically
    full_module_path = f"swarmauri.{module_name_lower}s.concrete"

    try:
        # Import the module dynamically
        module = importlib.import_module(full_module_path)

        # Get the list of class names from __all__
        class_names = getattr(module, "__all__", [])

        # Create a dictionary with class names and their corresponding class objects
        classes_dict = {
            class_name: getattr(module, class_name) for class_name in class_names
        }

        return classes_dict
    except ImportError as e:
        print(f"Error importing module {full_module_path}: {e}")
        raise ModuleNotFoundError(f"Resource '{module_name}' is not registered.")
    except AttributeError as e:
        print(f"Error accessing class in {full_module_path}: {e}")
        raise e


def get_class_from_module(module_name: str, class_name: str):
    """
    Dynamically imports a module and retrieves the class name of the module.

    :param module_name: The name of the module (e.g., "parsers", "agent").
    :return: The class name of the module.
    """
    # Convert module name to lowercase to ensure consistency
    module_name_lower = module_name.lower()

    # Construct the full module path dynamically
    full_module_path = f"swarmauri.{module_name_lower}s.concrete"

    try:
        # Import the module dynamically
        module = importlib.import_module(full_module_path)

        # Get the list of class names from __all__
        class_names = getattr(module, "__all__", [])

        if not class_names:
            raise AttributeError(f"No classes found in module {full_module_path}")

        for cls_name in class_names:
            if cls_name == class_name:
                return getattr(module, class_name)
        return None

    except ImportError as e:
        print(f"Error importing module {full_module_path}: {e}")
        raise ModuleNotFoundError(f"Resource '{module_name}' is not found.")
    except AttributeError as e:
        print(f"Error accessing class in {full_module_path}: {e}")
        raise e
