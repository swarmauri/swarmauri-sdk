"""Generic evaluator pool package."""

from .GenericEvaluatorPool import GenericEvaluatorPool

__all__ = ["GenericEvaluatorPool"]

try:  # pragma: no cover - version retrieval
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover - py38 fallback
    from importlib_metadata import PackageNotFoundError, version

try:  # pragma: no cover - dynamic
    __version__ = version("swarmauri_evaluatorpool_generic")
except PackageNotFoundError:  # pragma: no cover - local
    __version__ = "0.0.0"
