"""Client model for the authentication service."""

from __future__ import annotations

import re
import uuid
from typing import Final
from urllib.parse import urlparse

from tigrbl_auth.deps import ClientBase, hook_ctx, relationship

from ..crypto import hash_pw
from ..rfc.rfc8252 import (
    RFC8252_SPEC_URL,
    is_native_redirect_uri,
    validate_native_redirect_uri,
)
from ..runtime_cfg import settings

_CLIENT_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9\-_]{8,64}$")


class Client(ClientBase):
    __table_args__ = ({"schema": "authn"},)

    tenant = relationship("Tenant", back_populates="clients")

    @hook_ctx(ops=("create", "update"), phase="PRE_HANDLER")
    async def _hash_secret(cls, ctx):
        payload = ctx.get("payload") or {}
        secret = payload.pop("client_secret", None)
        if secret:
            payload["client_secret_hash"] = hash_pw(secret)

    @classmethod
    def new(
        cls,
        tenant_id: uuid.UUID,
        client_id: str,
        client_secret: str,
        redirects: list[str],
    ):
        if not _CLIENT_ID_RE.fullmatch(client_id):
            raise ValueError("invalid client_id format")
        if settings.enforce_rfc8252:
            for uri in redirects:
                parsed = urlparse(uri)
                if is_native_redirect_uri(uri):
                    validate_native_redirect_uri(uri)
                elif parsed.scheme == "http":
                    raise ValueError(
                        f"redirect URI not permitted for native apps per RFC 8252: {RFC8252_SPEC_URL}"
                    )
        secret_hash = hash_pw(client_secret)
        try:
            obj_id: uuid.UUID | str = uuid.UUID(client_id)
        except ValueError:
            obj_id = client_id
        return cls(
            tenant_id=tenant_id,
            id=obj_id,
            client_secret_hash=secret_hash,
            redirect_uris=" ".join(redirects),
        )

    def verify_secret(self, plain: str) -> bool:
        from ..crypto import verify_pw  # local import to avoid cycle

        return verify_pw(plain, self.client_secret_hash)


__all__ = ["Client", "_CLIENT_ID_RE"]
