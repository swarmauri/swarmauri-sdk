# peagen/storage_adapters/__init__.py
"""Factory helpers for storage adapters."""

from urllib.parse import urlparse
from peagen.plugin_registry import registry


def make_adapter_for_uri(uri: str):
    scheme = urlparse(uri).scheme or "file"  # 'file' if path like /home/...
    try:
        adapter_cls = registry["storage_adapters"][scheme]
    except KeyError:
        raise ValueError(f"No storage adapter registered for scheme '{scheme}'")
    if not hasattr(adapter_cls, "from_uri"):
        raise TypeError(f"{adapter_cls.__name__} lacks required from_uri()")
    return adapter_cls.from_uri(uri)
