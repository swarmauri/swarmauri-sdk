from .PromptSampler import PromptSampler

__all__ = ["PromptSampler"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_prompt_sampler")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
