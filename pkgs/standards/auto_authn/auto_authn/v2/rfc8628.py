"""Device Authorization Grant helpers and endpoint (RFC 8628).

This module implements utility helpers and the ``/device_authorization``
endpoint for the OAuth 2.0 Device Authorization Grant as defined in
RFC 8628.  The feature can be toggled via ``settings.enable_rfc8628`` and is
only mounted on the FastAPI application when enabled.

See RFC 8628: https://www.rfc-editor.org/rfc/rfc8628
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4
import re
import secrets
import string
from typing import Any, Dict, Final, Literal

from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel

from .runtime_cfg import settings

# Character set for user_code per RFC 8628 §6.1 (uppercase letters and digits)
_USER_CODE_CHARSET: Final = string.ascii_uppercase + string.digits
# Accept codes of length 8 or greater to match RFC 8628 recommendations
_USER_CODE_RE: Final = re.compile(r"^[A-Z0-9]{8,}$")

# Public URL of the RFC for reference in logs or documentation
RFC8628_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8628"


# ---------------------------------------------------------------------------
#  In-memory device authorization store
# ---------------------------------------------------------------------------
router = APIRouter()

DEVICE_CODES: Dict[str, Dict[str, Any]] = {}
DEVICE_VERIFICATION_URI = "https://example.com/device"
DEVICE_CODE_EXPIRES_IN = 600  # seconds
DEVICE_CODE_INTERVAL = 5  # seconds


class DeviceAuthIn(BaseModel):
    """Request body for device authorization."""

    client_id: str
    scope: str | None = None


class DeviceAuthOut(BaseModel):
    """Response body for device authorization."""

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class DeviceGrantForm(BaseModel):
    """Form model for the device_code grant at the token endpoint."""

    grant_type: Literal["urn:ietf:params:oauth:grant-type:device_code"]
    device_code: str
    client_id: str


@router.post("/device_authorization", response_model=DeviceAuthOut)
async def device_authorization(body: DeviceAuthIn) -> DeviceAuthOut:
    """Issue a new device and user code pair."""

    if not settings.enable_rfc8628:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "device authorization disabled")

    device_code = uuid4().hex
    user_code = uuid4().hex[:8]
    verification_uri = DEVICE_VERIFICATION_URI
    verification_uri_complete = f"{verification_uri}?user_code={user_code}"
    expires_at = datetime.utcnow() + timedelta(seconds=DEVICE_CODE_EXPIRES_IN)
    DEVICE_CODES[device_code] = {
        "user_code": user_code,
        "client_id": body.client_id,
        "expires_at": expires_at,
        "interval": DEVICE_CODE_INTERVAL,
        "authorized": False,
        "sub": None,
        "tid": None,
    }
    return DeviceAuthOut(
        device_code=device_code,
        user_code=user_code,
        verification_uri=verification_uri,
        verification_uri_complete=verification_uri_complete,
        expires_in=DEVICE_CODE_EXPIRES_IN,
        interval=DEVICE_CODE_INTERVAL,
    )


def approve_device_code(device_code: str, sub: str, tid: str) -> None:
    """Mark a device code as authorized (testing helper)."""

    if device_code in DEVICE_CODES:
        DEVICE_CODES[device_code]["authorized"] = True
        DEVICE_CODES[device_code]["sub"] = sub
        DEVICE_CODES[device_code]["tid"] = tid


def include_rfc8628(app: FastAPI) -> None:
    """Attach the RFC 8628 router to *app* if enabled."""

    if settings.enable_rfc8628 and not any(
        route.path == "/device_authorization" for route in app.routes
    ):
        app.include_router(router)


def generate_user_code(length: int = 8) -> str:
    """Return a user_code suitable for RFC 8628 §6.1.

    ``length`` defaults to the minimum 8 characters recommended by the spec
    and must be positive.  The resulting code uses only uppercase letters and
    digits for ease of transcription.
    """

    if length <= 0:
        raise ValueError("length must be positive")
    return "".join(secrets.choice(_USER_CODE_CHARSET) for _ in range(length))


def validate_user_code(code: str) -> bool:
    """Return ``True`` if *code* conforms to RFC 8628 §6.1.

    When ``settings.enable_rfc8628`` is ``False`` the check is skipped and
    ``True`` is returned to allow clients that do not implement the Device
    Authorization Grant.
    """

    if not settings.enable_rfc8628:
        return True
    return bool(_USER_CODE_RE.fullmatch(code))


def generate_device_code() -> str:
    """Return a high-entropy ``device_code`` per RFC 8628 §6.3."""

    # 32 bytes of randomness yields a 43-character URL-safe string
    return secrets.token_urlsafe(32)


__all__ = [
    "generate_user_code",
    "validate_user_code",
    "generate_device_code",
    "DeviceAuthIn",
    "DeviceAuthOut",
    "DeviceGrantForm",
    "DEVICE_CODES",
    "approve_device_code",
    "include_rfc8628",
    "router",
    "RFC8628_SPEC_URL",
]
