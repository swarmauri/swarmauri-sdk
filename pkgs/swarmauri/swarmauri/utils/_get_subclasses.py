from swarmauri.utils.LazyLoader import LazyLoader


def get_classes_from_module(module):
    import inspect

    classes = {}
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, LazyLoader):
            obj = obj._load_class()  # Load the class from LazyLoader
        if inspect.isclass(obj):
            classes[name] = obj
    return classes


def get_class_from_module(module, class_name):
    import inspect

    if hasattr(module, class_name):
        obj = getattr(module, class_name)
        if isinstance(obj, LazyLoader):
            obj = obj._load_class()
        if inspect.isclass(obj):
            return obj
    return None
