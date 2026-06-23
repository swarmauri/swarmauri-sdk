from .FileSystemSkill import FileSystemSkill

__all__ = ["FileSystemSkill"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_skill_filesystem")
except PackageNotFoundError:
    __version__ = "0.0.0"
