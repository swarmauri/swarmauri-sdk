![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/layout-engine-atoms/">
        <img src="https://img.shields.io/pypi/dm/layout-engine-atoms" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine_atoms/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine_atoms.svg"/></a>
    <a href="https://pypi.org/project/layout-engine-atoms/">
        <img src="https://img.shields.io/pypi/pyversions/layout-engine-atoms" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/layout-engine-atoms/">
        <img src="https://img.shields.io/pypi/l/layout-engine-atoms" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/layout-engine-atoms/">
        <img src="https://img.shields.io/pypi/v/layout-engine-atoms?label=layout-engine-atoms&color=green" alt="PyPI - layout-engine-atoms"/></a>
</p>

---

# Layout Engine Atoms

`layout-engine-atoms` packages Swarmauri's canonical UI atom presets for the [`layout-engine`](../layout_engine) runtime. Each preset maps a semantic role to a front-end module, export, version, and default props so downstream applications can bootstrap view-models without hand-curating every mapping.

> **Python compatibility:** officially supports Python 3.10, 3.11, and 3.12.

## Features

- **Curated presets** – ships ready-to-use role mappings covering common KPI, chart, data, and layout atoms.
- **Typed contracts** – builds on `layout-engine`'s `AtomSpec` models to validate module, export, and default prop shapes.
- **Composable registries** – helper utilities load presets into `AtomRegistry` instances or dictionaries for manifest pipelines.
- **Configurable overrides** – extend or replace built-ins by layering custom atoms on top of the defaults.

## Installation

```bash
# uv
uv add layout-engine-atoms

# pip
pip install layout-engine-atoms
```

## Usage

```python
from layout_engine_atoms import DEFAULT_ATOMS, build_registry

# Inspect the shipped presets
for role, spec in DEFAULT_ATOMS.items():
    print(role, spec.module, spec.export)

# Create a registry that layout-engine can consume
registry = build_registry()

# Register an override before passing to layout_engine
registry.override(
    "dashboard.hero",
    module="@layout-app/atoms",
    defaults={"accent": "violet"},
)
```

See [`examples/basic_usage.py`](../layout_engine/examples/basic_usage.py) for how manifests consume registries to merge props with layout metadata.

## Development

```bash
uv sync --all-extras
uv run --directory experimental/layout_engine_atoms --package layout-engine-atoms ruff check .
uv run --directory experimental/layout_engine_atoms --package layout-engine-atoms pytest -q
```

## License

Apache License 2.0. See [LICENSE](./LICENSE) for full terms.
