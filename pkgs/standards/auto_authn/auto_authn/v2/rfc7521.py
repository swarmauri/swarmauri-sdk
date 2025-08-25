"""RFC 7521 - Assertion Framework for OAuth 2.0 Client Authentication and Authorization Grants.

This module provides helpers for handling OAuth 2.0 assertions. The feature can
be toggled with the ``AUTO_AUTHN_ENABLE_RFC7521`` environment variable.
"""

from .runtime_cfg import settings

RFC7521_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc7521"


def extract_client_assertion(params: dict) -> tuple[str, str]:
    """Extract ``client_assertion`` and ``client_assertion_type`` from *params*.

    Raises:
        RuntimeError: If RFC 7521 support is disabled.
        KeyError: If required parameters are missing.
    """
    if not settings.enable_rfc7521:
        raise RuntimeError("RFC 7521 support disabled")
    return params["client_assertion"], params["client_assertion_type"]


__all__ = ["extract_client_assertion", "RFC7521_SPEC_URL"]
