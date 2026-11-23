from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "cells": [],
    "metadata": {},
}

result = JupyterValidateNotebookTool()(notebook=notebook)
print(result)
