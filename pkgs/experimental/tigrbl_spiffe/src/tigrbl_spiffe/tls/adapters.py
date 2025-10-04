from __future__ import annotations

import httpx
from typing import Any

async def httpx_client_with_tls(base_url: str, tls_helper: Any) -> httpx.AsyncClient:
    """Return an AsyncClient configured with TLS contexts built by tls_helper.

    NOTE: This is a placeholder; client cert/key installation depends on your environment.

    """
    _ = await tls_helper.client_context()  # currently unused placeholder
    return httpx.AsyncClient(base_url=base_url, timeout=10.0)
