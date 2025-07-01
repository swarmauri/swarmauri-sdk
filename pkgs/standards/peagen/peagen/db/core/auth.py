"""API Key authentication module"""

from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from peagen.db.core.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    """Validate the API key from the request header"""
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing in request header",
        )

    valid_keys = [settings.api_key_1, settings.api_key_2, settings.api_key_3]

    valid_keys = [key for key in valid_keys if key]

    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API authentication not configured - no valid API keys",
        )

    if api_key_header not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key"
        )

    return api_key_header
