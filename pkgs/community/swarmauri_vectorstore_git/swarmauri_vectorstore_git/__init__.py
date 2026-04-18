from .GitVectorStore import GitVectorStore

__all__ = ["GitVectorStore"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_vectorstore_git")
except PackageNotFoundError:
    __version__ = "0.0.0"
