from importlib.metadata import PackageNotFoundError, version

from .memory_storage_adapter import MemoryStorageAdapter

__all__ = ["MemoryStorageAdapter"]

try:
    __version__ = version("swarmauri_storage_memory")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
