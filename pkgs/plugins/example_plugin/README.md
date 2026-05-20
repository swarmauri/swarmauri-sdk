![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swm_example_plugin/">
        <img src="https://static.pepy.tech/badge/swm_example_plugin/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/example_plugin/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/example_plugin.svg"/></a>
    <a href="https://pypi.org/project/swm_example_plugin/">
        <img src="https://img.shields.io/pypi/pyversions/swm_example_plugin" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swm_example_plugin/">
        <img src="https://img.shields.io/pypi/l/swm_example_plugin" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swm_example_plugin/">
        <img src="https://img.shields.io/pypi/v/swm_example_plugin?label=swm_example_plugin&color=green" alt="PyPI - swm_example_plugin"/></a>
</p>
---

The Swarmauri Example Plugin is a lightweight reference package that shows how to
ship a plugin ready for the Swarmauri ecosystem. It demonstrates how to declare
entry points, surface metadata, and structure tests so that new plugin projects
start from a fully configured baseline that supports Python 3.10 through 3.12.

## Features

- **Entry-point wiring** - exposes the `swarmauri.plugins` group so your agent
  classes can be discovered automatically once implemented.
- **Ready-to-publish metadata** - includes keywords, classifiers, and long
  descriptions wired directly into `pyproject.toml`.
- **Version helpers** - surfaces `__version__` and `__long_desc__` constants so
  documentation and tooling can introspect the package after installation.
- **Testing scaffold** - ships with baseline unit tests verifying version
  resolution to encourage a test-first development workflow.

## Installation

### Using `uv`

```bash
uv add swm-example-plugin
```

### Using `pip`

```bash
pip install swm-example-plugin
```

## Usage

### Inspect published metadata

```python
from swm_example_plugin import __long_desc__, __version__

print(__version__)
print(__long_desc__.splitlines()[0])
```

### Discover the registered entry point

```python
from importlib.metadata import entry_points

for ep in entry_points(group="swarmauri.plugins"):
    if ep.name == "example_agent":
        print(ep.name, "->", ep.value)
        break
```

This skeleton intentionally leaves the actual agent implementation up to you.
Replace the target specified in the entry point with your concrete class to wire
custom functionality into the Swarmauri plugin registry.

## Project Resources

- Source: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/example_plugin>
- Documentation: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/plugins/example_plugin#readme>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>
- Releases: <https://github.com/swarmauri/swarmauri-sdk/releases>
- Discussions: <https://github.com/orgs/swarmauri/discussions>
