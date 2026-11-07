import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .ScrollFileTool import ScrollFileTool

__all__ = ["ScrollFileTool"]

try:
    __version__ = version("swarmauri_tool_scrollfile")
except PackageNotFoundError:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    match = re.search(
        r'^version\s*=\s*"([^"]+)"',
        pyproject.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    __version__ = match.group(1) if match else "0.0.0"
