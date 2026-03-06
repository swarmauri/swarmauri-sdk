
from __future__ import annotations
from typing import Any

async def _noop_async(obj: object | None, ctx: Any) -> None:
    return None

def _noop_sync(obj: object | None, ctx: Any) -> None:
    return None

_REGISTRY = {
    ('txn','begin'): ('sys.tx.begin', _noop_sync),
    ('txn','commit'): ('sys.tx.commit', _noop_async),
    ('handler','crud'): ('sys.handler.persistence', _noop_async),
}

def get(domain: str, subject: str):
    return _REGISTRY[(domain, subject)]
