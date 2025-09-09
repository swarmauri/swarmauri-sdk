
<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplay/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterdisplay" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterdisplay/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterdisplay.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplay/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterdisplay" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplay/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterdisplay" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplay/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterdisplay?label=swarmauri_tool_jupyterdisplay&color=green" alt="PyPI - swarmauri_tool_jupyterdisplay"/></a>
</p>

---

# Swarmauri Tool Jupyter Display

The `JupyterDisplayTool` is a component that leverages IPython display functionality to render data with a variety of rich representations. It inherits from `ToolBase` and integrates with the Swarmauri framework's tool architecture.

## Description

`JupyterDisplayTool` is a tool that displays data in a Jupyter environment using IPython's rich display capabilities. It supports multiple data formats, including plain text, HTML, images, and LaTeX.

### Attributes

- **version (str)**: The version of the JupyterDisplayTool.
- **parameters (List[Parameter])**: A list of parameters defining the expected inputs.
- **name (str)**: The name of the tool.
- **description (str)**: A brief description of the tool's functionality.
- **type (Literal["JupyterDisplayTool"])**: The type identifier for the tool.

### Usage

The tool can be used to render various types of data in a Jupyter notebook. Below is an example of how to use the `JupyterDisplayTool`:

```python
display_tool = JupyterDisplayTool()
display_tool("<b>Hello, world!</b>", "html")
```

This will display the provided HTML content in the Jupyter notebook.

### Methods

- `__call__(self, data: str, data_format: str = "auto") -> Dict[str, str]`: Renders the provided data in the Jupyter environment using IPython's display.

#### Arguments

- `data (str)`: The data to be displayed. Could be text, HTML, a path to an image, or LaTeX.
- `data_format (str, optional)`: The format of the data. Defaults to 'auto'. Supported values are 'text', 'html', 'image', and 'latex'.

#### Returns

- `Dict[str, str]`: A dictionary containing the status of the operation ("success" or "error") and a corresponding message.

Example:

```python
display_tool = JupyterDisplayTool()
result = display_tool("<b>Hello, world!</b>", "html")
print(result)  # {'status': 'success', 'message': 'Data displayed successfully.'}
```
