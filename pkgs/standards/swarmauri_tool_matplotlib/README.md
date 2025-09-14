
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_matplotlib/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_matplotlib" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_matplotlib/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_matplotlib.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_matplotlib/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_matplotlib" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_matplotlib/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_matplotlib" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_matplotlib/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_matplotlib?label=swarmauri_tool_matplotlib&color=green" alt="PyPI - swarmauri_tool_matplotlib"/></a>
</p>

---

# Swarmauri Tool Matplotlib

A Swarmauri package that provides tools for generating plots using Matplotlib. Includes support for basic plots and CSV data visualization.

## Installation

```bash
pip install swarmauri_tool_matplotlib
```

## Usage

### Basic Plotting
```python
from swarmauri.tools.MatplotlibTool import MatplotlibTool

# Create a tool instance
tool = MatplotlibTool()

# Generate a line plot
result = tool(
    plot_type="line",
    x_data=[1, 2, 3],
    y_data=[4, 5, 6],
    title="Line Plot",
    x_label="X-axis",
    y_label="Y-axis",
    save_path="plot.png"
)
```

### CSV Data Plotting
```python
from swarmauri_tool_matplotlib.MatplotlibCsvTool import MatplotlibCsvTool

# Create a CSV tool instance
csv_tool = MatplotlibCsvTool()

# Generate a plot from CSV data
result = csv_tool(
    csv_file="data.csv",
    x_column="x",
    y_column="y",
    output_file="csv_plot.png"
)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

