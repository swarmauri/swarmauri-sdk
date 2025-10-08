![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/layout-engine-swarmakit-vue/">
        <img src="https://img.shields.io/pypi/dm/layout-engine-swarmakit-vue" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine_swarmakit_vue/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/layout_engine_swarmakit_vue.svg"/></a>
    <a href="https://pypi.org/project/layout-engine-swarmakit-vue/">
        <img src="https://img.shields.io/pypi/pyversions/layout-engine-swarmakit-vue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/layout-engine-swarmakit-vue/">
        <img src="https://img.shields.io/pypi/l/layout-engine-swarmakit-vue" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/layout-engine-swarmakit-vue/">
        <img src="https://img.shields.io/pypi/v/layout-engine-swarmakit-vue?label=layout-engine-swarmakit-vue&color=green" alt="PyPI - layout-engine-swarmakit-vue"/></a>
</p>

---

# Layout Engine × Swarmakit Vue Presets

`layout-engine-swarmakit-vue` delivers a ready-to-use preset catalog that connects the
[`layout-engine`](../layout_engine) contracts to Swarmauri's `@swarmakit/vue`
component library. It ships curated roles, strongly-typed defaults, and utilities
for compiling and serving manifests with Vue-powered widgets.

> **Python compatibility:** officially supports Python 3.10, 3.11, and 3.12.

## Features

- **Vue component presets** – opinionated role mappings that point directly to the
  `@swarmakit/vue` modules, complete with ergonomic defaults.
- **Authoring widgets** – Python-friendly helpers for building tiles that represent
  Swarmakit Vue atoms inside `layout-engine` manifests.
- **Runtime helpers** – shortcuts for compiling, rendering, and serving pages with
  the Swarmakit presets applied.
- **Uvicorn-ready demo app** – ship a FastAPI app that renders Swarmakit Vue
  components using `layout-engine` manifests.

## Installation

Choose the toolchain you prefer.

```bash
# uv
uv add layout-engine-swarmakit-vue

# pip
pip install layout-engine-swarmakit-vue
```

The package declares a runtime dependency on `layout-engine` and pulls in the
server extras (FastAPI + Uvicorn) so you can serve manifests immediately.

## Usage

```python
from layout_engine.authoring.ctx.builder import TableCtx
from layout_engine_swarmakit_vue import (
    SwarmakitAvatar,
    SwarmakitDataGrid,
    SwarmakitNotification,
    SwarmakitProgressBar,
    compile_swarmakit_table,
)

layout = TableCtx()
row = layout.row()
row.col(size="m").add(
    SwarmakitAvatar("avatar.alice", initials="AL", image_src="https://example.com/avatar.png"),
)
row.col(size="l").add(
    SwarmakitDataGrid(
        "grid.sales",
        headers=["Region", "Revenue"],
        data=[["NA", "$1.2M"], ["EMEA", "$980k"]],
    ),
)

manifest = compile_swarmakit_table(layout)
```

See `examples/serve.py` for a FastAPI + Uvicorn walkthrough that renders the
components server-side while exposing the manifest JSON for client hydration.

## License

Apache License 2.0. See [LICENSE](./LICENSE) for the full terms.
