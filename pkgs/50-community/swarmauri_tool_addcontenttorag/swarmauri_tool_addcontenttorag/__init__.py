from importlib.metadata import PackageNotFoundError, version

from .AddContentToRAGTool import AddContentToRAGTool

try:
    __version__ = version("swarmauri_tool_addcontenttorag")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["AddContentToRAGTool"]
