from importlib.metadata import PackageNotFoundError, version

from .NvidiaNIMModel import NvidiaNIMModel
from .NvidiaNIMToolModel import NvidiaNIMToolModel

try:
    __version__ = version("swarmauri_llm_nvidia_nim")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["NvidiaNIMModel", "NvidiaNIMToolModel"]
