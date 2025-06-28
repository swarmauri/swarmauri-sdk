from __future__ import annotations

import uuid
from typing import Any, Dict, Type, TypeVar

import httpx

from pydantic import TypeAdapter

from peagen.protocols import Request, Response

R = TypeVar("R")


def rpc_post(
    url: str,
    method: str,
    params: Dict[str, Any],
    *,
    id: str | None = None,
    timeout: float = 30.0,
    result_model: Type[R] | None = None,
) -> Response[R | Dict[str, Any]]:
    """Send a JSON-RPC request and return a typed :class:`Response`."""
    envelope = Request(id=id or str(uuid.uuid4()), method=method, params=params)
    resp = httpx.post(url, json=envelope.model_dump(), timeout=timeout)
    resp.raise_for_status()
    if result_model is not None:
        adapter = TypeAdapter(Response[result_model])  # type: ignore[index]
    else:
        adapter = TypeAdapter(Response[Dict[str, Any]])
    return adapter.validate_python(resp.json())
