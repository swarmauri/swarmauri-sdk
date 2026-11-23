from swarmauri_tool_jupyterexporthtml import JupyterExportHtmlTool

notebook_json = """
{
  "cells": [{"cell_type": "markdown", "metadata": {}, "source": ["# Demo"]}],
  "metadata": {},
  "nbformat": 4,
  "nbformat_minor": 5
}
"""

tool = JupyterExportHtmlTool()
result = tool(notebook_json=notebook_json)

print(result["exported_html"][:200])
