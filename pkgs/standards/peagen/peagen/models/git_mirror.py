from __future__ import annotations

from pydantic import BaseModel, HttpUrl, SecretStr


class GitMirror(BaseModel):
    """Configuration details for a mirrored Git repository."""

    base_url: HttpUrl
    token: SecretStr | None = None
    owner: str | None = None
