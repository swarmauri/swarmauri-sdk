![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tests_component

[![Downloads](https://static.pepy.tech/badge/swarmauri_tests_component/month)](https://pepy.tech/project/swarmauri_tests_component)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_component.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_component/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_tests_component/)
[![License](https://img.shields.io/pypi/l/swarmauri_tests_component)](https://pypi.org/project/swarmauri_tests_component/)
[![Release](https://img.shields.io/pypi/v/swarmauri_tests_component?label=release&color=green)](https://pypi.org/project/swarmauri_tests_component/)

`swarmauri_tests_component` is a pytest plugin that generates the universal
proofs required of concrete Swarmauri components. Packages declare their
components once and receive separately reported construction, identity,
resource-family, serialization, and dynamic-registration tests.

## Features

- Generates five consistent proofs for every declared component.
- Verifies component family inheritance, `type`, `name`, and `resource`.
- Verifies JSON round trips while supporting intentionally excluded secrets.
- Verifies `ComponentBase.register_type(...)` registration.
- Reports each component/proof pair as an independent pytest item.
- Leaves provider-specific functionality in the owning package's normal tests.

## Installation

With `uv`:

```bash
uv add --dev swarmauri_tests_component
```

With `pip`:

```bash
pip install swarmauri_tests_component
```

## Usage

Declare package-owned components in `tests/conftest.py`:

```python
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_tests_component import ComponentSpec
from your_package import YourModel


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            component_class=YourModel,
            init_kwargs={"api_key": "test-key", "allowed_models": ["*"]},
            expected_resource="LLM",
            expected_name="provider/model",
            base_class=LLMBase,
            round_trip_overrides={"api_key": "test-key"},
            excluded_fields=("api_key",),
        )
    ]
```

Run the package's normal pytest command. The installed `pytest11` entry point
loads the plugin automatically:

```bash
pytest
```

The plugin intentionally does not prove provider behavior. Keep prediction,
tool execution, multimodal payload, image generation, async, batching, retry,
and integration tests in the provider package.

## License

Licensed under the [Apache License 2.0](LICENSE).
