from swarmauri_tool_jupyterreadnotebook.JupyterReadNotebookTool import (
    JupyterReadNotebookTool,
)


__all__ = ["JupyterReadNotebookTool"]

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_tool_jupyterreadnotebook")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"
