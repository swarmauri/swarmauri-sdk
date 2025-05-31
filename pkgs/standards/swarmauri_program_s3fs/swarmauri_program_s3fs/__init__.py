from .S3fsProgram import S3fsProgram

__all__ = ["S3fsProgram"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_program_s3fs")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
