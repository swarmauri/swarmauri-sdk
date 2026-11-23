from .ConstantTimeEvaluator import ConstantTimeEvaluator

__all__ = ["ConstantTimeEvaluator"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_evaluator_constanttime")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
