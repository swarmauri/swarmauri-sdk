<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri-typing/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-typing" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/typing/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/typing.svg"/></a>
    <a href="https://pypi.org/project/swarmauri-typing/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-typing" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri-typing/">
        <img src="https://img.shields.io/pypi/l/swarmauri-typing" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri-typing/">
        <img src="https://img.shields.io/pypi/v/swarmauri-typing?label=swarmauri-typing&color=green" alt="PyPI - swarmauri-typing"/></a>
</p>

---

# Swarmauri Typing

The Swarmauri Typing Library provides advanced type utilities for Python, enabling more expressive and flexible type annotations. It includes tools for creating intersection and union types dynamically.

## Features

- **Intersection Types**: Create intersection types that combine multiple classes.

```python
from typing import Type, TypeVar, Union, Any, Annotated, Tuple

T = TypeVar("T")

class IntersectionMetadata:
    def __init__(self, classes: Tuple[Type[T]]):
        self.classes = classes

    def __repr__(self):
        return f"IntersectionMetadata(classes={self.classes!r})"

class Intersection(type):
    def __class_getitem__(cls, classes: Union[Type, Tuple[Type, ...]]) -> type:
        if not isinstance(classes, tuple):
            classes = (classes,)

        common = set(classes[0].__mro__)
        for c in classes[1:]:
            common.intersection_update(c.__mro__)

        ordered_common = [c for c in classes[0].__mro__ if c in common]

        if not ordered_common:
            return Annotated[Any, IntersectionMetadata(classes=(classes))]
        else:
            union_type = Union[tuple(ordered_common)]
            return Annotated[union_type, IntersectionMetadata(classes=(classes))]
```

- **Union Factory**: Dynamically create union types based on a provided function.

```python
from typing import Type, TypeVar, Callable, List, Union, Any, Annotated, get_args, Optional

T = TypeVar("T")

class UnionFactoryMetadata:
    def __init__(self, data: Any, name: Optional[str] = None):
        self.data = data
        self.name = name or self.__class__.__name__

    def __repr__(self):
        return f"UnionFactoryMetadata(name={self.name!r}, data={self.data!r})"

class UnionFactory:
    def __init__(self, bound: Callable[[Type[T]], List[type]], name: str = None, annotation_extenders: List[Any] = None):
        self.name = name or self.__class__.__name__
        self._union_types_getter = bound
        self._annotation_extenders = annotation_extenders or []

    def _add_metadata(self, annotated_type: Any, new_metadata: Any) -> Any:
        if not (hasattr(annotated_type, '__origin__') and annotated_type.__origin__ is Annotated):
            return Annotated[annotated_type, new_metadata]

        args = get_args(annotated_type)
        base_type = args[0]
        old_metadata = args[1:]
        return Annotated[base_type, *old_metadata, new_metadata]

    def __getitem__(self, input_data: Union[Type[T], str]) -> type:
        if isinstance(input_data, str):
            model_name = input_data
        else:
            model_name = input_data.__name__

        union_members = self._union_types_getter(model_name)

        if not union_members:
            final_annotated = Annotated[Any, UnionFactoryMetadata(data=model_name, name=self.name)]
        else:
            union_type = Union[tuple(union_members)]
            final_annotated = Annotated[union_type, UnionFactoryMetadata(data=model_name, name=self.name)]

            for extension in self._annotation_extenders:
                final_annotated = self._add_metadata(final_annotated, extension)

        return final_annotated
```

## Getting Started

To start using the Swarmauri Typing Library, include it as a module in your Python project. Ensure you have Python 3.10 or later installed.

### Steps to install via pypi

```sh
pip install swarmauri-typing
```

### Usage Example

```python
from swarmauri_typing import Intersection, UnionFactory

# Example of using Intersection
class A: pass
class B: pass

IntersectionType = Intersection[A, B]

# Example of using UnionFactory
def my_types_getter(name: str):
    return [A, B]

union_factory = UnionFactory(my_types_getter)
MyUnion = union_factory["MyModel"]
```


## Contributing

Contributions are welcome! If you'd like to add a new feature, fix a bug, or improve documentation, kindly go through the [contributions guidelines](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) first.

