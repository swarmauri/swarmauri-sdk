from .BM25FScorer import BM25FScorer
from .FsVectorStore import FsVectorStore

__all__ = ["BM25FScorer", "FsVectorStore"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_vectorstore_fs")
except PackageNotFoundError:
    __version__ = "0.0.0"
