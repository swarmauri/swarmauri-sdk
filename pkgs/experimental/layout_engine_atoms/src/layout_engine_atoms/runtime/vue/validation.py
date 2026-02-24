"""Security validation utilities for the Vue runtime."""

from __future__ import annotations

import logging
import re
from typing import Any, Mapping

from fastapi import HTTPException

logger = logging.getLogger(__name__)


class PayloadValidationError(ValueError):
    """Raised when payload validation fails."""

    pass


def validate_payload_against_schema(
    payload: Mapping[str, Any], schema: Mapping[str, Any]
) -> None:
    """Validate payload against a JSON schema.

    Args:
        payload: The payload data to validate
        schema: JSON schema to validate against

    Raises:
        PayloadValidationError: If validation fails

    Note:
        This is a basic implementation. For production use, consider
        using jsonschema library for full JSON Schema validation.
    """
    if not schema:
        return

    # Basic schema validation - type checking
    if "type" in schema:
        expected_type = schema["type"]
        if expected_type == "object" and not isinstance(payload, Mapping):
            raise PayloadValidationError(f"Expected object, got {type(payload).__name__}")
        elif expected_type == "array" and not isinstance(payload, (list, tuple)):
            raise PayloadValidationError(f"Expected array, got {type(payload).__name__}")

    # Check required fields
    if "required" in schema and isinstance(schema["required"], list):
        missing_fields = [
            field for field in schema["required"] if field not in payload
        ]
        if missing_fields:
            raise PayloadValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

    # Validate properties
    if "properties" in schema and isinstance(payload, Mapping):
        for key, value in payload.items():
            if key in schema["properties"]:
                prop_schema = schema["properties"][key]
                _validate_property(key, value, prop_schema)


def _validate_property(
    key: str, value: Any, prop_schema: Mapping[str, Any]
) -> None:
    """Validate a single property against its schema."""
    if "type" in prop_schema:
        expected_type = prop_schema["type"]
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": (list, tuple),
            "object": Mapping,
        }

        if expected_type in type_map:
            expected_python_type = type_map[expected_type]
            if not isinstance(value, expected_python_type):
                raise PayloadValidationError(
                    f"Field '{key}': expected {expected_type}, got {type(value).__name__}"
                )

    # Check enum constraints
    if "enum" in prop_schema:
        if value not in prop_schema["enum"]:
            raise PayloadValidationError(
                f"Field '{key}': value must be one of {prop_schema['enum']}"
            )

    # Check string length
    if isinstance(value, str):
        if "minLength" in prop_schema and len(value) < prop_schema["minLength"]:
            raise PayloadValidationError(
                f"Field '{key}': string too short (min {prop_schema['minLength']})"
            )
        if "maxLength" in prop_schema and len(value) > prop_schema["maxLength"]:
            raise PayloadValidationError(
                f"Field '{key}': string too long (max {prop_schema['maxLength']})"
            )

    # Check numeric ranges
    if isinstance(value, (int, float)):
        if "minimum" in prop_schema and value < prop_schema["minimum"]:
            raise PayloadValidationError(
                f"Field '{key}': value below minimum ({prop_schema['minimum']})"
            )
        if "maximum" in prop_schema and value > prop_schema["maximum"]:
            raise PayloadValidationError(
                f"Field '{key}': value above maximum ({prop_schema['maximum']})"
            )


# XSS Protection patterns
DANGEROUS_JS_PATTERNS = [
    # Script tags
    re.compile(r"<script[^>]*>", re.IGNORECASE),
    # Event handlers
    re.compile(r"\bon\w+\s*=", re.IGNORECASE),
    # javascript: protocol
    re.compile(r"javascript\s*:", re.IGNORECASE),
    # data: protocol with potentially dangerous content
    re.compile(r"data:text/html", re.IGNORECASE),
    # eval and similar functions
    re.compile(r"\b(eval|Function|setTimeout|setInterval)\s*\(", re.IGNORECASE),
    # Suspicious string concatenation that might build code
    re.compile(r"(document\.write|innerHTML|outerHTML)\s*[+\[]", re.IGNORECASE),
]


def validate_client_setup_code(code: str) -> None:
    """Validate client setup code for potential security issues.

    Args:
        code: JavaScript code to validate

    Raises:
        ValueError: If dangerous patterns are detected

    Note:
        This is a basic XSS protection. For production, consider:
        - Content Security Policy (CSP) headers
        - Trusted Types API
        - Code review process for client setup
    """
    if not code or not isinstance(code, str):
        return

    for pattern in DANGEROUS_JS_PATTERNS:
        if pattern.search(code):
            raise ValueError(
                f"Client setup code contains potentially dangerous pattern: "
                f"'{pattern.pattern}'. This code will be injected directly "
                f"into the HTML and must be carefully reviewed for security issues."
            )


def sanitize_string_for_logging(value: str, max_length: int = 100) -> str:
    """Sanitize a string for safe logging by truncating and removing sensitive patterns.

    Args:
        value: The string to sanitize
        max_length: Maximum length before truncation

    Returns:
        Sanitized string safe for logging
    """
    if not value:
        return ""

    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length] + "..."

    # Remove potential secrets (tokens, passwords, etc.)
    # This is a basic implementation - extend as needed
    value = re.sub(r'("password"|"token"|"secret"|"api_key")\s*:\s*"[^"]*"',
                   r'\1: "[REDACTED]"', value, flags=re.IGNORECASE)

    return value


def validate_event_payload(
    event_id: str, payload: Mapping[str, Any], schema: Mapping[str, Any] | None
) -> None:
    """Validate an event payload and raise HTTPException if invalid.

    Args:
        event_id: The event identifier
        payload: The payload to validate
        schema: Optional JSON schema to validate against

    Raises:
        HTTPException: With status 400 if validation fails
    """
    if not schema:
        return

    try:
        validate_payload_against_schema(payload, schema)
    except PayloadValidationError as e:
        logger.warning(
            f"Payload validation failed for event '{event_id}': {str(e)}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid payload: {str(e)}",
        ) from e
