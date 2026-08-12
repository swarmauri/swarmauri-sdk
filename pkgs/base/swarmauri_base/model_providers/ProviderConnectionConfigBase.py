"""Compatibility import for the renamed provider connection value object."""

from warnings import warn

from .ProviderConnectionConfig import ProviderConnectionConfig

warn(
    "ProviderConnectionConfigBase is deprecated; use ProviderConnectionConfig",
    DeprecationWarning,
    stacklevel=2,
)

ProviderConnectionConfigBase = ProviderConnectionConfig

__all__ = ["ProviderConnectionConfigBase"]
