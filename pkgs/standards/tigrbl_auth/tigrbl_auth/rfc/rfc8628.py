"""Device Authorization Grant helpers and endpoint (RFC 8628).

This module implements utility helpers and the ``/device_authorization``
endpoint for the OAuth 2.0 Device Authorization Grant as defined in
RFC 8628.  The feature can be toggled via ``settings.enable_rfc8628`` and is
only mounted on the FastAPI application when enabled.

See RFC 8628: https://www.rfc-editor.org/rfc/rfc8628
"""

from __future__ import annotations

import re
import secrets
import string
from typing import Final, Literal, TYPE_CHECKING

from tigrbl_auth.deps import BaseModel, AsyncSession

from ..runtime_cfg import settings

if TYPE_CHECKING:  # pragma: no cover
    pass

# Character set for user_code per RFC 8628 §6.1 (uppercase letters and digits)
_USER_CODE_CHARSET: Final = string.ascii_uppercase + string.digits
# Accept codes of length 8 or greater to match RFC 8628 recommendations
_USER_CODE_RE: Final = re.compile(r"^[A-Z0-9]{8,}$")

# Public URL of the RFC for reference in logs or documentation
RFC8628_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc8628"


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


async def approve_device_code(
    device_code: str, sub: str, tid: str, db: AsyncSession
) -> None:
    """Mark a device code as authorized (testing helper)."""

    from ..orm import DeviceCode

    obj = await DeviceCode.handlers.read.core({"db": db, "obj_id": device_code})
    if obj:
        await DeviceCode.handlers.update.core(
            {
                "db": db,
                "obj": obj,
                "payload": {"authorized": True, "user_id": sub, "tenant_id": tid},
            }
        )


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
    "approve_device_code",
    "RFC8628_SPEC_URL",
    "DEVICE_VERIFICATION_URI",
    "DEVICE_CODE_EXPIRES_IN",
    "DEVICE_CODE_INTERVAL",
]
