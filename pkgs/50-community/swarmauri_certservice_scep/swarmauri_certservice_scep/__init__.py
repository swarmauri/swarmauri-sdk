"""SCEP certificate service plugin for Swarmauri.

Provides the :class:`ScepCertService` for performing certificate enrollment via
the Simple Certificate Enrollment Protocol.
"""

from .ScepCertService import ScepCertService

__all__ = ["ScepCertService"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:  # pragma: no cover
    __version__ = version("swarmauri_certservice_scep")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
