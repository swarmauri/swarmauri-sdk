"""Utilities for OAuth 2.0 for Native Apps (RFC 8252).

This module provides helpers to validate redirect URIs as required by
RFC 8252. Native applications are restricted to using either private-use
URI schemes or the loopback interface with an HTTP(S) scheme and a
dynamically chosen port. Redirect URIs that fall outside of these
patterns are considered non-compliant. Enforcement of these rules can be
toggled via ``runtime_cfg.Settings.enforce_rfc8252`` which is controlled
by the ``AUTO_AUTHN_ENFORCE_RFC8252`` environment variable.

See RFC 8252: https://www.rfc-editor.org/rfc/rfc8252
"""

from __future__ import annotations

from urllib.parse import urlparse
from typing import Final

RFC8252_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8252"

# Hosts that resolve to the loopback interface as defined by RFC 8252 §7.3
_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def is_native_redirect_uri(uri: str) -> bool:
    """Return ``True`` if *uri* satisfies RFC 8252 redirect URI rules.

    RFC 8252 section 7 defines two valid redirect URI patterns for native
    applications:

    * Private-use URI schemes (anything other than ``http`` or ``https``).
    * Loopback interface redirects using ``http`` or ``https`` with hosts
      ``127.0.0.1``, ``localhost`` or ``[::1]`` and any port.
    """

    parsed = urlparse(uri)
    if parsed.scheme in {"http", "https"}:
        host = parsed.hostname or ""
        return host in _LOOPBACK_HOSTS
    # Any non HTTP(S) scheme is considered a private-use scheme
    return bool(parsed.scheme)


def validate_native_redirect_uri(uri: str) -> None:
    """Validate *uri* for RFC 8252 compliance.

    Raises ``ValueError`` if the URI does not meet the requirements for
    native applications.
    """

    if not is_native_redirect_uri(uri):
        raise ValueError(
            f"redirect URI not permitted for native apps per RFC 8252: {RFC8252_SPEC_URL}"
        )


__all__ = ["is_native_redirect_uri", "validate_native_redirect_uri", "RFC8252_SPEC_URL"]
