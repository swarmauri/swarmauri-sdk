from swarmauri_tool_jupyterexportmarkdown import JupyterExportMarkdownTool

notebook = {
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": ["# Demo"]},
        {
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": ["print('hello')"],
        },
    ],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 5,
}

result = JupyterExportMarkdownTool()(notebook_json=notebook)
print(result["exported_markdown"])
