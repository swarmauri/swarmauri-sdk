from .PromptTemplateSampler import PromptTemplateSampler

__all__ = ["PromptTemplateSampler"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_prompt_template_sampler")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
