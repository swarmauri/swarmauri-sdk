from swarmauri_tool_jupyterexportlatex import JupyterExportLatexTool

notebook = {
    "cells": [
        {
            "cell_type": "code",
            "metadata": {},
            "source": ["1 + 1"],
            "outputs": [],
        }
    ],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 5,
}

result = JupyterExportLatexTool()(
    notebook_node=notebook,
    to_pdf=False,
)

print(result["latex_content"][:200])
