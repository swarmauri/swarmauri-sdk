# swarmauri_standard/utils/lazy_loader.py

import importlib
import warnings
from typing import Any, Optional, Type, TypeVar

T = TypeVar('T')

class LazyLoader:
    """
    A class for lazy-loading a specific class from a module. The module is
    not actually imported until the first time you access an attribute or
    call this object. If import fails, a warning is issued and an exception
    is raised when you attempt to use the class.
    """
    def __init__(self, module_name: str, class_name: str):
        self.module_name = module_name
        self.class_name = class_name
        self._loaded_class: Optional[Type[Any]] = None
        self._import_error: Optional[Exception] = None

    def _load_class(self) -> Optional[Type[Any]]:
        if self._loaded_class is not None or self._import_error is not None:
            return self._loaded_class

        try:
            module = importlib.import_module(self.module_name)
            self._loaded_class = getattr(module, self.class_name)
        except ModuleNotFoundError as e:
            warnings.warn(
                f"Module '{self.module_name}' not found. Please install the "
                "necessary dependencies to enable this functionality.",
                category=ImportWarning
            )
            self._import_error = e
        except AttributeError as e:
            warnings.warn(
                f"Class '{self.class_name}' was not found in module '{self.module_name}'.",
                category=ImportWarning
            )
            self._import_error = e
        except ImportError as e:
            warnings.warn(
                f"Unable to import '{self.module_name}' due to: {e}",
                category=ImportWarning
            )
            self._import_error = e

        return self._loaded_class

    def __getattr__(self, item: str) -> Any:
        loaded_class = self._load_class()
        if loaded_class is None:
            raise self._import_error  # type: ignore
        return getattr(loaded_class, item)

    def __call__(self, *args, **kwargs) -> Any:
        loaded_class = self._load_class()
        if loaded_class is None:
            raise self._import_error  # type: ignore
        return loaded_class(*args, **kwargs)

    def __instancecheck__(self, instance: Any) -> bool:
        loaded_class = self._load_class()
        if loaded_class:
            return isinstance(instance, loaded_class)
        return False

    def __subclasscheck__(self, subclass: Type[Any]) -> bool:
        loaded_class = self._load_class()
        if loaded_class:
            return issubclass(subclass, loaded_class)
        return False

    def __dir__(self) -> list[str]:
        loaded_class = self._load_class()
        if loaded_class:
            return dir(loaded_class)
        return super().__dir__()

    def __repr__(self) -> str:
        loaded_class = self._load_class()
        if loaded_class:
            return repr(loaded_class)
        return f"<LazyLoader for {self.class_name}>"
