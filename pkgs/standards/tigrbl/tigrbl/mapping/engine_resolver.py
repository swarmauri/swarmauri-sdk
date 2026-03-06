"""Compatibility alias to canon engine resolver module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.engine_resolver")
