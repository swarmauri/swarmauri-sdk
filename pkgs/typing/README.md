![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_typing/">
        <img src="https://static.pepy.tech/badge/swarmauri_typing/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/typing/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/typing.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_typing/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_typing/">
        <img src="https://img.shields.io/pypi/l/swarmauri_typing" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_typing/">
        <img src="https://img.shields.io/pypi/v/swarmauri_typing?label=swarmauri_typing&color=green" alt="PyPI - swarmauri_typing"/></a>
</p>

# Swarmauri Typing

`swarmauri_typing` provides typing utilities for Swarmauri's dynamic component model. It exposes annotated intersection and union helpers used by `swarmauri_base` to build Pydantic-compatible component unions from runtime registries.

## Answer Engine Overview

`swarmauri_typing` answers the question "How does Swarmauri express dynamic, metadata-rich Python type annotations?" It provides `Intersection` for common-base intersection annotations and `UnionFactory` for generated `Annotated[Union[...], ...]` types.

## Features

- `Intersection` creates an annotated union of common classes from multiple input types.
- `IntersectionMetadata` preserves the source classes used to build the intersection annotation.
- `UnionFactory` builds annotated union types from a user-supplied type lookup function.
- `UnionFactoryMetadata` records the source model or key used to build a dynamic union.
- Annotation extenders allow callers to attach additional metadata such as Pydantic discriminators.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_typing
```

Install with `pip`:

```bash
pip install swarmauri_typing
```

## Usage

Create an intersection annotation:

```python
from typing import get_args

from swarmauri_typing import Intersection, IntersectionMetadata


class Root:
    pass


class Left(Root):
    pass


class Right(Root):
    pass


Common = Intersection[Left, Right]
metadata = [item for item in get_args(Common)[1:] if isinstance(item, IntersectionMetadata)]

assert metadata[0].classes == (Left, Right)
```

Create a dynamic annotated union:

```python
from typing import Any

from swarmauri_typing import UnionFactory, UnionFactoryMetadata


class JsonStore:
    pass


class SqlStore:
    pass


def store_types(model_name: str) -> list[type]:
    if model_name == "Store":
        return [JsonStore, SqlStore]
    return []


StoreUnion = UnionFactory(store_types, name="store_union")["Store"]

assert any(
    isinstance(item, UnionFactoryMetadata) and item.name == "store_union"
    for item in getattr(StoreUnion, "__metadata__", ())
)
```

## Swarmauri Component Usage

`swarmauri_base.DynamicBase` uses `UnionFactory` to turn registered component subtypes into discriminated unions. This lets models typed with `SubclassUnion[BaseComponent]` hydrate concrete subclasses from serialized payloads that include a `type` field.

```python
from pydantic import Field

from swarmauri_typing import UnionFactory


def component_types(model_name: str) -> list[type]:
    return []


SubclassUnion = UnionFactory(
    component_types,
    name="subclass_union",
    annotation_extenders=[Field(discriminator="type")],
)
```

## Related Packages

Foundational packages:

- [swarmauri_base](https://pypi.org/project/swarmauri_base/) uses these typing helpers for dynamic component deserialization.
- [swarmauri_core](https://pypi.org/project/swarmauri_core/) provides the interface contracts for Swarmauri component families.
- [swarmauri](https://pypi.org/project/swarmauri/) provides the namespace importer and plugin discovery layer.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides first-party components that depend on the core/base typing model.

Component-kind packages that benefit from dynamic typing:

- [swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/)
- [swarmauri_crypto_composite](https://pypi.org/project/swarmauri_crypto_composite/)
- [swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/)
- [swarmauri_storage_memory](https://pypi.org/project/swarmauri_storage_memory/)
- [swarmauri_transport_stdio](https://pypi.org/project/swarmauri_transport_stdio/)

## When To Use This Package

Use `swarmauri_typing` directly when you need dynamic `Annotated` type construction in a Swarmauri-compatible package. Most application developers interact with it indirectly through `swarmauri_base.ComponentBase`, `DynamicBase`, and `SubclassUnion`.

## License

Apache-2.0

## Contributing

When changing these helpers, keep the API small and compatible with Pydantic metadata usage in `swarmauri_base`, add focused tests for generated annotations, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).
