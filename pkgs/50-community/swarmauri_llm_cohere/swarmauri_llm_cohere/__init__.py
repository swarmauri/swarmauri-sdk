from .CohereModel import CohereModel
from .CohereToolModel import CohereToolModel

__all__ = ["CohereModel", "CohereToolModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_cohere")
except PackageNotFoundError:
    __version__ = "0.0.0"
