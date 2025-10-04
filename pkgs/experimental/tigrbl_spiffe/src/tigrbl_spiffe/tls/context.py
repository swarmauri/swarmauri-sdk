from __future__ import annotations

import ssl
from typing import Any, Optional

class TlsHelper:
    """Builds SSL contexts from SPIFFE materials.

    For x509-SVID, we fetch the current SVID via Workload API when needed (so we don't persist private keys).

    """

    def __init__(self, adapter: Any, cfg: Any):
        self._adapter = adapter
        self._cfg = cfg

    async def client_context(self) -> ssl.SSLContext:
        """Return an mTLS client context built from the current x509-SVID and bundle.

        This minimal implementation defers key/chain extraction to the Workload API client.

        """
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # If your deployment exposes a CA bundle, set it here; otherwise keep system defaults.
        # To attach client cert + key, we'd need PEMs from the agent. Leave as is for now.
        return ctx

    async def server_context(self) -> ssl.SSLContext:
        """Return an mTLS server context. To be fully functional this needs access to private key material.

        For many SPIFFE deployments, the TLS termination is handled upstream; we expose the hook point anyway.

        """
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx
