from swarmauri_tool_jupyterexportpython import JupyterExportPythonTool

notebook = {
    "cells": [
        {
            "cell_type": "code",
            "metadata": {},
            "source": "print('hello')",
            "outputs": [],
        }
    ],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 5,
}

result = JupyterExportPythonTool()(notebook=notebook)
print(result["exported_script"])
