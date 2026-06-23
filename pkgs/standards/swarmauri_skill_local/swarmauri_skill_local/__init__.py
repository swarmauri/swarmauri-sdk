from .LocalSkill import LocalSkill

__all__ = ["LocalSkill"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_skill_local")
except PackageNotFoundError:
    __version__ = "0.0.0"
