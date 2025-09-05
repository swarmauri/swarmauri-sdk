"""Factory helpers for storage adapters."""

from urllib.parse import urlparse
import warnings

from peagen.plugins import PluginManager
from peagen._utils.config_loader import resolve_cfg

warnings.warn(
    "peagen.plugins.storage_adapters is deprecated; use peagen.plugins.git_filters instead",
    DeprecationWarning,
    stacklevel=2,
)


def make_adapter_for_uri(uri: str):
    """Return a storage adapter instance based on *uri* scheme."""
    scheme = urlparse(uri).scheme or "file"  # 'file' if path like /home/...
    pm = PluginManager(resolve_cfg())
    try:
        adapter_cls = pm._resolve_spec("storage_adapters", scheme)
    except KeyError:
        raise ValueError(f"No storage adapter registered for scheme '{scheme}'")
    if not hasattr(adapter_cls, "from_uri"):
        raise TypeError(f"{adapter_cls.__name__} lacks required from_uri()")
    return adapter_cls.from_uri(uri)


__all__ = ["make_adapter_for_uri"]
