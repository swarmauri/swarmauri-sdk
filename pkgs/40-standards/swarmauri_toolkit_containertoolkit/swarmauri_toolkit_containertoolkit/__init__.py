from .ContainerToolkit import ContainerToolkit

__all__ = ["ContainerToolkit"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_toolkit_containertoolkit")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
