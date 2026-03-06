"""Compatibility alias to canon router resource proxy module."""

from importlib import import_module
import sys

sys.modules[__name__] = import_module("tigrbl_canon.mapping.router.resource_proxy")
