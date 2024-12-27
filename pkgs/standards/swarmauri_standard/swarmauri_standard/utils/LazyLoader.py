import importlib

class LazyLoader:
    def __init__(self, module_name, class_name):
        self.module_name = module_name
        self.class_name = class_name
        self._loaded_class = None

    def _load_class(self):
        if self._loaded_class is None:
            try:
                module = importlib.import_module(self.module_name)
                self._loaded_class = getattr(module, self.class_name)
            except ImportError:
                print(
                    f"Warning: The module '{self.module_name}' is not available. "
                    f"Please install the necessary dependencies to enable this functionality."
                )
                self._loaded_class = None
            except AttributeError:
                print(
                    f"Warning: The class '{self.class_name}' was not found in module '{self.module_name}'."
                )
                self._loaded_class = None
        return self._loaded_class

    def __getattr__(self, item):
        loaded_class = self._load_class()
        if loaded_class is None:
            raise ImportError(f"Unable to load class {self.class_name} from {self.module_name}")
        return getattr(loaded_class, item)

    def __call__(self, *args, **kwargs):
        loaded_class = self._load_class()
        if loaded_class is None:
            raise ImportError(f"Unable to load class {self.class_name} from {self.module_name}")
        return loaded_class(*args, **kwargs)
