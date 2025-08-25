"""Helpers for OAuth 2.0 Rich Authorization Requests (RFC 9396).

This module implements minimal validation for the ``authorization_details``
parameter described in RFC 9396. The parameter is defined as a JSON array of
objects where each object **MUST** contain a ``type`` member identifying the
kind of authorization being requested.
"""

from __future__ import annotations

import json
from typing import Any, List, Dict


def parse_authorization_details(
    value: str | List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Parse and validate an ``authorization_details`` parameter.

    Parameters
    ----------
    value:
        The raw parameter value as received in a request. This may be a JSON
        encoded string or a Python list of dictionaries.

    Returns
    -------
    list of dict
        The parsed authorization detail objects.

    Raises
    ------
    ValueError
        If the input is not valid per RFC 9396 §2.1.
    """

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError("authorization_details must be valid JSON") from exc
    else:
        parsed = value

    if not isinstance(parsed, list):
        raise ValueError("authorization_details must be a JSON array")

    for item in parsed:
        if not isinstance(item, dict) or "type" not in item:
            raise ValueError(
                "each authorization detail must be an object with a 'type' member"
            )
    return parsed
