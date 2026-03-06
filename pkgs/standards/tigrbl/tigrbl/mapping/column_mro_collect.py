"""Compatibility alias to canon column MRO collector module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.column_mro_collect")
