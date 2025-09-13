
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_toolkit_jupytertoolkit" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_jupytertoolkit/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_toolkit_jupytertoolkit.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_toolkit_jupytertoolkit" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/">
        <img src="https://img.shields.io/pypi/l/swarmauri_toolkit_jupytertoolkit" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_toolkit_jupytertoolkit/">
        <img src="https://img.shields.io/pypi/v/swarmauri_toolkit_jupytertoolkit?label=swarmauri_toolkit_jupytertoolkit&color=green" alt="PyPI - swarmauri_toolkit_jupytertoolkit"/></a>
</p>

---

# Swarmauri Toolkit Jupytertoolkit

A unified toolkit for aggregating standalone jupyter notebook tools.

## Installation

To install `swarmauri_toolkit_jupytertoolkit`, run the following command:

```bash
pip install swarmauri_toolkit_jupytertoolkit
```

## Usage

To use `swarmauri_toolkit_jupytertoolkit`, you can import it into your Python script or Jupyter Notebook:

```python
from swarmauri_toolkit_jupytertoolkit import JupyterToolkit
```

You can then create an instance of the `JupyterToolkit` class:

```python
toolkit = JupyterToolkit()
```

The `JupyterToolkit` class provides a centralized management system for all integrated tools. You can add and remove tools from the toolkit using the `add_tool` and `remove_tool` methods:

```python
toolkit.add_tool("JupyterClearOutputTool")
toolkit.remove_tool("JupyterClearOutputTool")
```

You can also configure and customize tool settings using the `configure_tool` method:

```python
toolkit.configure_tool("JupyterClearOutputTool", {"option": "value"})
```

The `JupyterToolkit` class also provides an intuitive and user-friendly interface for accessing and using integrated tools. You can access the interface by calling the `display` method:

```python
toolkit.display()
```

This will display the toolkit interface in the Jupyter Notebook.

## Contributing

To contribute to `swarmauri_toolkit_jupytertoolkit`, please fork the repository and submit a pull request. Please ensure that your contributions adhere to the project's coding standards and guidelines.

## License

`swarmauri_toolkit_jupytertoolkit` is licensed under the Apache License 2.0. Please see the LICENSE file for more information.

## Authors

* Jacob Stewart <jacob@swarmauri.com>

## Acknowledgments

* The `swarmauri_toolkit_jupytertoolkit` project was made possible by the contributions of the Swarmauri community.
* The project is built on top of the Jupyter Notebook framework and its dependencies.
