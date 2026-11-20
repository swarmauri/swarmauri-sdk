from swarmauri_tool_jupyterwritenotebook import JupyterWriteNotebookTool

tool = JupyterWriteNotebookTool()
result = tool(
    notebook_data={
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [],
    },
    output_file="artifacts/output.ipynb",
)

print(result)
