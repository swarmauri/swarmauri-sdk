"""Jollof: generic plugin management."""

from .plugin_manager import PluginManager
from .registry import PluginDomainRegistry

__all__ = ["PluginManager", "PluginDomainRegistry"]
