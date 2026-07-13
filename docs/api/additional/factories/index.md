# Factories

Factory classes construct and configure component instances from type identifiers and parameters.

## Hierarchy

```
FactoryBase
├── AgentFactory
├── ToolFactory
├── VectorStoreFactory
├── LLMFactory
├── EmbeddingFactory
├── ChunkerFactory
├── DocumentStoreFactory
└── ...
```

All factories inherit from `FactoryBase`, which defines the shared registration and creation surface.

## Method Surface

| Method | Description |
|--------|-------------|
| `create(type: str, **kwargs)` | Instantiate a registered type by name |
| `register(type: str, cls)` | Bind a type name to a concrete class |
| `unregister(type: str)` | Remove a type registration |
| `list_types()` | Return registered type names |
| `get_class(type: str)` | Resolve type name to class without instantiating |

## Specialize / Extend

Subclass `FactoryBase` and register domain-specific types:

```python
from swarmauri.factories.FactoryBase import FactoryBase

class MyComponentFactory(FactoryBase):
    def __init__(self):
        super().__init__()
        self.register("my_type", MyComponent)

factory = MyComponentFactory()
instance = factory.create("my_type", name="example")
```

Override `create` only when construction requires multi-step setup beyond `cls(**kwargs)`.
