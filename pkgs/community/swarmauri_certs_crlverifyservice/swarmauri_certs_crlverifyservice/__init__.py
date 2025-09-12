"""Expose the :class:`CrlVerifyService` for external use.

The CRL verification service validates X.509 certificates against provided
certificate revocation lists.
"""

from .CrlVerifyService import CrlVerifyService

__all__ = ["CrlVerifyService"]
