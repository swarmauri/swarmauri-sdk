"""Compatibility alias to canon model helpers module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.model_helpers")
