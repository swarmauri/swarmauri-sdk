# FactoryBase

```{eval-rst}
.. currentmodule:: swarmauri_base.factories.factory_base

.. autoclass:: FactoryBase
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Hierarchy

```text
object
└── FactoryBase
```

`FactoryBase` is the abstract root for all factories in Swarmauri. Concrete factories subclass it and implement type registration and instance construction.

## Signatures

```python
class FactoryBase(ABC):
    def __init__(self) -> None: ...

    @abstractmethod
    def create(self, type_: str, **kwargs: Any) -> Any:
        """Construct an instance for the given registered type key."""

    def register(self, type_: str, cls: type) -> None:
        """Register a concrete class under a type key."""

    def unregister(self, type_: str) -> None:
        """Remove a previously registered type key."""

    def get_type(self, type_: str) -> type | None:
        """Return the class registered for ``type_``, or ``None``."""

    def list_types(self) -> list[str]:
        """Return all registered type keys."""
```

## Extension Example

```python
from typing import Any
from swarmauri_base.factories.factory_base import FactoryBase


class WidgetFactory(FactoryBase):
    def __init__(self) -> None:
        super().__init__()
        self._registry: dict[str, type] = {}

    def register(self, type_: str, cls: type) -> None:
        self._registry[type_] = cls

    def unregister(self, type_: str) -> None:
        self._registry.pop(type_, None)

    def get_type(self, type_: str) -> type | None:
        return self._registry.get(type_)

    def list_types(self) -> list[str]:
        return list(self._registry)

    def create(self, type_: str, **kwargs: Any) -> Any:
        cls = self.get_type(type_)
        if cls is None:
            raise KeyError(f"Unknown type: {type_!r}")
        return cls(**kwargs)


# Usage
factory = WidgetFactory()
factory.register("button", Button)
widget = factory.create("button", label="OK")
```
