<p align="center">
  <img src="https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg" alt="Swarmauri logotype" width="420" />
</p>

<h1 align="center">Swarmauri Example Plugin</h1>

<p align="center">
  <a href="https://pypi.org/project/swm-example-plugin/"><img src="https://img.shields.io/pypi/dm/swm-example-plugin?style=for-the-badge" alt="PyPI - Downloads" /></a>
  <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/example_plugin/"><img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/example_plugin.svg?style=for-the-badge" alt="Repository views" /></a>
  <a href="https://pypi.org/project/swm-example-plugin/"><img src="https://img.shields.io/pypi/pyversions/swm-example-plugin?style=for-the-badge" alt="Supported Python versions" /></a>
  <a href="https://pypi.org/project/swm-example-plugin/"><img src="https://img.shields.io/pypi/l/swm-example-plugin?style=for-the-badge" alt="License" /></a>
  <a href="https://pypi.org/project/swm-example-plugin/"><img src="https://img.shields.io/pypi/v/swm-example-plugin?style=for-the-badge&label=swm-example-plugin" alt="Latest release" /></a>
</p>

---

The Swarmauri Example Plugin is a lightweight reference package that shows how to
ship a plugin ready for the Swarmauri ecosystem. It demonstrates how to declare
entry points, surface metadata, and structure tests so that new plugin projects
start from a fully configured baseline that supports Python 3.10 through 3.12.

## Features

- **Entry-point wiring** – exposes the `swarmauri.plugins` group so your agent
  classes can be discovered automatically once implemented.
- **Ready-to-publish metadata** – includes keywords, classifiers, and long
  descriptions wired directly into `pyproject.toml`.
- **Version helpers** – surfaces `__version__` and `__long_desc__` constants so
  documentation and tooling can introspect the package after installation.
- **Testing scaffold** – ships with baseline unit tests verifying version
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

- Source: <https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/example_plugin>
- Documentation: <https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/plugins/example_plugin#readme>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>
- Releases: <https://github.com/swarmauri/swarmauri-sdk/releases>
