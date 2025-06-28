from __future__ import annotations

import uuid
from typing import Any, Dict

import httpx

from peagen.protocols import Request, TASK_SUBMIT


def rpc_post(
    url: str,
    method: str,
    params: Dict[str, Any],
    *,
    id: str | None = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Send a JSON-RPC request using :class:`peagen.protocols.Request`."""
    if method == TASK_SUBMIT and "task" not in params:
        params = {"task": params}
    envelope = Request(id=id or str(uuid.uuid4()), method=method, params=params)
    resp = httpx.post(url, json=envelope.model_dump(), timeout=timeout)
    resp.raise_for_status()
    return resp.json()
