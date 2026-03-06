"""Compatibility alias to canon core resolver module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.core_resolver")
