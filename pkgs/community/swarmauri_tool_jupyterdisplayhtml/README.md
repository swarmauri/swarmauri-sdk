
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplayhtml/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterdisplayhtml" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterdisplayhtml/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterdisplayhtml.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplayhtml/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterdisplayhtml" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplayhtml/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterdisplayhtml" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterdisplayhtml/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterdisplayhtml?label=swarmauri_tool_jupyterdisplayhtml&color=green" alt="PyPI - swarmauri_tool_jupyterdisplayhtml"/></a>
</p>

---

# Swarmauri Tool Jupyter Display Html

A tool designed to render HTML content within a Jupyter Notebook using IPython's HTML display method.

## Installation

1. Ensure you have Python 3.10 or newer installed.  
2. Install from PyPI using your preferred package manager:

   • pip:
     pip install swarmauri_tool_jupyterdisplayhtml

   • Poetry:
     poetry add swarmauri_tool_jupyterdisplayhtml

This will pull down all required dependencies, including IPython for HTML display capabilities, and the Swarmauri Core/Base libraries for tool interaction.

## Usage

Once installed, import the JupyterDisplayHTMLTool class and invoke it to render HTML content in a Jupyter cell. Here is a simple example to get you started:

-------------------------------------------------------------------------------------------
Example usage:

from swarmauri_tool_jupyterdisplayhtml import JupyterDisplayHTMLTool

def main():
    # Instantiate the tool
    display_tool = JupyterDisplayHTMLTool()

    # Sample HTML content
    html_snippet = """
    <h1>Hello from Swarmauri!</h1>
    <p>This content is displayed using JupyterDisplayHTMLTool.</p>
    """

    # Call the tool with the HTML content
    result = display_tool(html_snippet)

    # The tool returns a dictionary with status and message
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")

if __name__ == "__main__":
    main()
-------------------------------------------------------------------------------------------

Running this script in a Jupyter Notebook cell will display the HTML heading and paragraph above the cell's output. The command line output after invocation will confirm whether the display was successful or if an error occurred.

## Extended Options

• Dynamic Updates: You can instantiate the tool once and call it multiple times with different HTML fragments to display updated content in different cells.  
• Integration with Other Tools: Because JupyterDisplayHTMLTool inherits from ToolBase, it integrates cleanly with other Swarmauri-based tools and workflows.  
• Error Handling: If an error occurs while rendering HTML, the returned dictionary will have "status" = "error" and a "message" describing the issue.

## Dependencies

• swarmauri_core (>=0.6.0.dev1): Provides core mechanics and decorators for registering this tool.  
• swarmauri_base (>=0.6.0.dev1): Supplies the base ToolBase class.  
• IPython: Used to display HTML content in a Jupyter environment.

For detailed version requirements, see the "pyproject.toml" file in this project. The code is written following PEP 8 guidelines, uses type hints, and includes docstrings to clarify functionality at every class and method level. Additional logs and comments assist in understanding critical points of the implementation.

---

Use this package to effortlessly render HTML content in a Jupyter environment and integrate the display process within your broader Swarmauri-based ecosystem.
