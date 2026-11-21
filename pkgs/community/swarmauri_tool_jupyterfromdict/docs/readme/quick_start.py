from swarmauri_tool_jupyterfromdict import JupyterFromDictTool

payload = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "cells": [],
    "metadata": {},
}

result = JupyterFromDictTool()(notebook_dict=payload)
print(result)
