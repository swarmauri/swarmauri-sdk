from .PyPDFTKParser import PyPDFTKParser


__all__ = ["PyPDFTKParser"]

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri-parser-pypdftk")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"
