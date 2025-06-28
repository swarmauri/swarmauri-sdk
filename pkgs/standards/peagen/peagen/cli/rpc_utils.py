from __future__ import annotations

import uuid
from typing import Any, Dict, Type

import httpx
from pydantic import BaseModel

from peagen.protocols import Request, Response, _registry


def rpc_post(
    url: str,
    method: str,
    params: BaseModel | Dict[str, Any],
    *,
    id: str | None = None,
    timeout: float = 30.0,
) -> Response:
    """Send a typed JSON-RPC request and return a :class:`Response`."""

    payload = (
        params.model_dump(mode="python") if isinstance(params, BaseModel) else params
    )
    envelope: Request = Request(
        id=id or str(uuid.uuid4()), method=method, params=payload
    )
    resp = httpx.post(url, json=envelope.model_dump(), timeout=timeout)
    resp.raise_for_status()

    data = resp.json()
    result_model: Type[BaseModel] | None = _registry.result_model(method)
    response_cls = Response[result_model] if result_model else Response
    return response_cls.model_validate(data)
