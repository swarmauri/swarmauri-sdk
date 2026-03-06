"""Compatibility alias to canon config resolver module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.config_resolver")
