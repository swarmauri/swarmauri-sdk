from importlib.metadata import PackageNotFoundError, version

from .QueryImageVectorStoreTool import QueryImageVectorStoreTool

try:
    __version__ = version("swarmauri_tool_queryimagevectorstore")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["QueryImageVectorStoreTool"]
