from __future__ import annotations

import uuid
from typing import Any, Dict

import httpx

from pydantic import BaseModel

from peagen.protocols import Request, Response


def rpc_post(
    url: str,
    method: str,
    params: Dict[str, Any] | BaseModel,
    *,
    id: str | None = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Send a JSON-RPC request using :class:`peagen.protocols.Request`."""
    if isinstance(params, BaseModel):
        params = params.model_dump(mode="json")
    envelope = Request(id=id or str(uuid.uuid4()), method=method, params=params)
    resp = httpx.post(url, json=envelope.model_dump(), timeout=timeout)
    resp.raise_for_status()
    raw = resp.json()
    return Response.model_validate(raw).model_dump()
