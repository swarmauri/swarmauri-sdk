"""
peagen.gateway.services.crouton_factory
=======================================

Small helper that returns a pre-configured **CroutonClient** for talking to
Peagen’s auto-generated CRUD REST API.

Configuration is driven by two environment variables:

  • PEAGEN_API_ROOT   – Base URL *up to* (but not including) the resource path.
                        Default: ``http://localhost:8001/api/v1``

  • PEAGEN_API_TOKEN  – Optional token appended as ``?token=…`` query parameter
                        on every request.

The helper keeps one *lazy singleton* for the sync client and one for the async
client so that callers don’t open a new HTTP connection pool each time.
"""

from __future__ import annotations

import os
import threading
from typing import Optional

from crouton_client import CroutonClient

# -------------------------------------------------------------------------- #
# Internal caches (lazy singletons)                                          #
# -------------------------------------------------------------------------- #
_sync_singleton: Optional[CroutonClient] = None
_async_singleton: Optional[CroutonClient] = None
_lock = threading.Lock()          # guard lazy init in multithread context


# -------------------------------------------------------------------------- #
# Helper – build a *fresh* CroutonClient                                     #
# -------------------------------------------------------------------------- #
def _build() -> CroutonClient:
    root  = os.getenv("PEAGEN_API_ROOT",  "http://localhost:8001/api/v1")
    token = os.getenv("PEAGEN_API_TOKEN") or None
    timeout = float(os.getenv("PEAGEN_API_TIMEOUT", "10.0"))

    return CroutonClient(API_ROOT=root, ACCESS_STRING=token, timeout=timeout)


# -------------------------------------------------------------------------- #
# Public API                                                                 #
# -------------------------------------------------------------------------- #
def client() -> CroutonClient:
    """
    Return a **singleton synchronous** CroutonClient.

    Callers should *not* close this client; it is owned by the factory.
    """
    global _sync_singleton
    if _sync_singleton is None:
        with _lock:
            if _sync_singleton is None:     # double-checked
                _sync_singleton = _build()
    return _sync_singleton


async def aclient() -> CroutonClient:
    """
    Return a **singleton asynchronous** CroutonClient.

    The underlying httpx.AsyncClient remains open for the process lifetime.
    """
    global _async_singleton
    if _async_singleton is None:
        with _lock:
            if _async_singleton is None:
                _async_singleton = _build()
    return _async_singleton


# convenience alias used in RPC modules
get_client = client
