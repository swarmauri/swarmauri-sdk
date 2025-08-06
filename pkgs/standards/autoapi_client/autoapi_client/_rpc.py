# autoapi_client/_rpc.py
from __future__ import annotations

import uuid
import json
import httpx
from typing import Any, TypeVar, overload, Protocol
from typing import runtime_checkable

T = TypeVar("T")


@runtime_checkable
class _Schema(Protocol[T]):  # anything with Pydantic-v2 interface
    @classmethod
    def model_validate(cls, data: Any) -> T: ...
    @classmethod
    def model_dump_json(cls, **kw) -> str: ...


class RPCMixin:
    """
    Mixin class providing JSON-RPC functionality for AutoAPIClient.
    """

    def _get_endpoint(self) -> str:
        """Get the endpoint URL."""
        return self._endpoint

    def _get_client(self) -> httpx.Client:
        """Get the HTTP client."""
        return self._client

    # ─────────── public high-level call helpers ────────────────────── #
    @overload
    def call(  # result with schema
        self,
        method: str,
        *,
        params: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def call(  # raw / no schema
        self,
        method: str,
        *,
        params: dict | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def call(
        self,
        method: str,
        *,
        params: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]] | None = None,
    ) -> Any:
        """
        Make a JSON-RPC call.

        Args:
            method: The RPC method name
            params: Parameters to send (dict or Pydantic schema)
            out_schema: Optional Pydantic schema for result validation

        Returns:
            The RPC result, optionally validated through out_schema

        Raises:
            RuntimeError: If the RPC returns an error
            httpx.HTTPStatusError: If the HTTP request fails
        """
        # ----- payload build ------------------------------------------------
        if isinstance(params, _Schema):  # pydantic in → dump to dict
            params_dict = json.loads(params.model_dump_json())
        else:
            # ensure plain dicts contain only JSON-serializable values
            params_dict = json.loads(json.dumps(params or {}, default=str))

        req = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params_dict,
            "id": str(uuid.uuid4()),
        }

        # ----- HTTP roundtrip ----------------------------------------------
        headers = {"Content-Type": "application/json"}
        headers.update(getattr(self, "_headers", {}))
        r = self._get_client().post(
            self._get_endpoint(),
            json=req,
            headers=headers,
        )

        r.raise_for_status()
        res = r.json()
        # ----- JSON-RPC error handling -------------------------------------
        if err := res.get("error"):
            code = err.get("code", -32000)
            msg = err.get("message", "Unknown error")
            raise RuntimeError(f"RPC error {code}: {msg}")

        result = res["result"]

        # ----- optional pydantic validation --------------------------------
        if out_schema is not None and result is not None:
            return out_schema.model_validate(result)  # type: ignore[return-value]
        return result
