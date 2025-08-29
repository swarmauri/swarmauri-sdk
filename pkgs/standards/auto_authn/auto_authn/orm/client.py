"""Client model for the authentication service."""

from __future__ import annotations

import re
import uuid
from typing import Final

from autoapi.v3.tables import Client as ClientBase
from autoapi.v3 import hook_ctx

from ..crypto import hash_pw
from ..rfc8252 import validate_native_redirect_uri
from ..runtime_cfg import settings

_CLIENT_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9\-_]{8,64}$")


class Client(ClientBase):
    __table_args__ = ({"schema": "authn"},)

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
                validate_native_redirect_uri(uri)
        secret_hash = hash_pw(client_secret)
        return cls(
            tenant_id=tenant_id,
            id=client_id,
            client_secret_hash=secret_hash,
            redirect_uris=" ".join(redirects),
        )

    def verify_secret(self, plain: str) -> bool:
        from ..crypto import verify_pw  # local import to avoid cycle

        return verify_pw(plain, self.client_secret_hash)


__all__ = ["Client", "_CLIENT_ID_RE"]
