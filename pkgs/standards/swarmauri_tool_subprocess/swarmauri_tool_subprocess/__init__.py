from importlib import metadata as _metadata

from .SubprocessTool import SubprocessTool

__all__ = ["SubprocessTool"]

try:
    __version__ = _metadata.version("swarmauri_tool_subprocess")
except _metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"