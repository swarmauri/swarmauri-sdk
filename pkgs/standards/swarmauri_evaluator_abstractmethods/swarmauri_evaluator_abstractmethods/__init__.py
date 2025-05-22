from .AbstractMethodsEvaluator import AbstractMethodsEvaluator

<<<<<<< HEAD
__all__ = [
    "AbstractMethodsEvaluator"
]
=======
__all__ = ["AbstractMethodsEvaluator"]
>>>>>>> upstream/mono/dev

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_evaluator_abstractmethods")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"