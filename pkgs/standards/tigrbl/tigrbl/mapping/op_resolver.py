"""Compatibility alias to canon op resolver module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.op_resolver")
