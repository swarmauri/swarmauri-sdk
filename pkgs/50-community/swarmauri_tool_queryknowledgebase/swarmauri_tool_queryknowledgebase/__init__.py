from importlib.metadata import PackageNotFoundError, version

from .QueryKnowledgeBaseTool import QueryKnowledgeBaseTool

try:
    __version__ = version("swarmauri_tool_queryknowledgebase")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["QueryKnowledgeBaseTool"]
