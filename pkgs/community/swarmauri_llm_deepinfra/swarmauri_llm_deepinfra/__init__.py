from .DeepInfraModel import DeepInfraModel

__all__ = ["DeepInfraModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_deepinfra")
except PackageNotFoundError:
    __version__ = "0.0.0"
