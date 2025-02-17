from .PersistentQdrantVectorStore import PersistentQdrantVectorStore
from .CloudQdrantVectorStore import CloudQdrantVectorStore

__all__ = ["PersistentQdrantVectorStore", "CloudQdrantVectorStore"]

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_vectorstore_qdrant")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"
