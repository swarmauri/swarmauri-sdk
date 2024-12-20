import importlib
import inspect
import logging

from swarmauri.utils.LazyLoader import LazyLoader


def get_classes_from_module(resource_name: str):
    """
    Pass something like 'llms' to import 'swarmauri.llms.concrete'
    and retrieve all loaded classes.
    """
    resource_name = resource_name.lower()

    full_module = f"swarmauri.{resource_name}s.concrete"
    module = importlib.import_module(full_module)

    classes = {}
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, LazyLoader):
            obj = obj._load_class()
        if inspect.isclass(obj):
            classes[name] = obj

    logging.info(f"Classes found in module {module}: {classes}")
    return classes


def get_class_from_module(resource_name, class_name):
    resource_name = resource_name.lower()

    full_module = f"swarmauri.{resource_name}s.concrete"
    module = importlib.import_module(full_module)

    if hasattr(module, class_name):
        obj = getattr(module, class_name)
        if isinstance(obj, LazyLoader):
            obj = obj._load_class()
        if inspect.isclass(obj):
            return obj
    return None
