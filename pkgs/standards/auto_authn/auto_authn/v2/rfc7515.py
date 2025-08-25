"""Utilities for JSON Web Signature (RFC 7515).

This module implements helpers for validating JWS structures as required by
RFC 7515. At present it focuses on verifying that the JOSE header includes the
``alg`` parameter and that it is not set to the unsecured ``none`` algorithm
per RFC 7515 §4.1.
"""

from __future__ import annotations

from typing import Any, Dict

import jwt
from jwt.exceptions import InvalidTokenError

RFC7515_SPEC_URL = "https://datatracker.ietf.org/doc/html/rfc7515"


def validate_jws_header(token: str) -> None:
    """Validate the JOSE header of *token*.

    Raises
    ------
    InvalidTokenError
        If the ``alg`` header parameter is missing or set to ``none`` in
        violation of RFC 7515 §4.1.
    """

    header: Dict[str, Any] = jwt.get_unverified_header(token)
    alg = header.get("alg")
    if not alg or alg.lower() == "none":
        raise InvalidTokenError("JWS alg header missing or 'none' per RFC 7515")
