"""
Canonical constructor for JSON-RPC **Request** objects.

• Guarantees that *method* is registered in the central transport registry.
• Validates *params* against the registered Params model.
• Returns a pydantic `Request[P]` object from peagen.transport.envelope.
"""
from __future__ import annotations

import uuid
from typing import Any, Mapping, cast

from pydantic import BaseModel, ValidationError

from ._registry import params_model                      # validated lookup
from .envelope import Request

# ---------- public exception ----------
class RPCBuildError(RuntimeError):
    """Raised when the Request cannot be assembled or validated."""


def _validated_params(method: str,
                      supplied: Mapping[str, Any] | BaseModel) -> Mapping[str, Any]:
    """Return a **dict** that passes the Params schema for *method*."""
    model_cls = params_model(method)
    if model_cls is None:                                 # unregistered RPC
        raise RPCBuildError(f"Method '{method}' is not registered")

    # Accept already-typed models OR raw dicts.
    try:
        model_inst: BaseModel = (
            supplied if isinstance(supplied, BaseModel) else model_cls(**supplied)
        )
    except ValidationError as exc:
        raise RPCBuildError(str(exc)) from exc

    return cast(Mapping[str, Any], model_inst.model_dump(mode="json"))


def build_jsonrpc_request(
    method: str,
    params: Mapping[str, Any] | BaseModel,
    *,
    id: str | None = None,
) -> Request[dict]:
    """
    Return a **validated** `Request[dict]` (jsonrpc = '2.0', extra = 'forbid').

    Parameters
    ----------
    method : Canonical constant from peagen.transport.jsonrpc_schemas.
    params : Dict or typed Params model.
    id     : Optional JSON-RPC id; str(uuid4()) if omitted.

    Raises
    ------
    RPCBuildError  –  unknown method or params invalid for that method.
    """
    safe_params = _validated_params(method, params)
    return Request(                                         # matches envelope.py
        id=id or str(uuid.uuid4()),
        method=method,
        params=safe_params,
    )
