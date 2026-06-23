from .SkillAgent import SkillAgent

__all__ = ["SkillAgent"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_agent_skill")
except PackageNotFoundError:
    __version__ = "0.0.0"
