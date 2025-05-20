from .SubprocessEvaluator import SubprocessEvaluator

<<<<<<< HEAD
__all__ = [
    "SubprocessEvaluator"
]
=======
__all__ = ["SubprocessEvaluator"]
>>>>>>> upstream/mono/dev

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_evaluator_subprocess")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
<<<<<<< HEAD
    __version__ = "0.0.0"
=======
    __version__ = "0.0.0"
>>>>>>> upstream/mono/dev
