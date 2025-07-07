# autoapi_client/__init__.py
from __future__ import annotations

import itertools, json, uuid, httpx
from typing import Any, Generic, TypeVar, overload, Protocol
from typing import runtime_checkable              # ← add


T = TypeVar("T")

@runtime_checkable   
class _Schema(Protocol[T]):            # anything with Pydantic-v2 interface
    @classmethod
    def model_validate(cls, data: Any) -> T: ...
    @classmethod
    def model_dump_json(cls, **kw) -> str: ...

# --------------------------------------------------------------------- #
class AutoAPIClient:
    """
    Tiny, dependency-free JSON-RPC client for AutoAPI.
    * Uses httpx for async / sync requests.
    * Generates ids, sets Content-Type, decodes error envelopes.
    * Optional pydantic schema validation on both params & result.
    """

    def __init__(self, endpoint: str, *, client: httpx.Client | None = None):
        self._endpoint = endpoint
        self._own      = client is None          # whether we manage its life
        self._client   = client or httpx.Client(timeout=10.0)
        self._id_iter  = itertools.count()

    # ─────────── public high-level call helpers ────────────────────── #
    @overload
    def call(                                        # result with schema
        self,
        method: str,
        *,
        params: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def call(                                        # raw / no schema
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

        # ----- payload build ------------------------------------------------
        if isinstance(params, _Schema):     # pydantic in → dump to dict
            params_dict = json.loads(params.model_dump_json())
        else:
            params_dict = params or {}

        req = {
            "jsonrpc": "2.0",
            "method":  method,
            "params":  params_dict,
            "id":      next(self._id_iter),
        }

        # ----- HTTP roundtrip ----------------------------------------------
        r = self._client.post(
            self._endpoint,
            json=req,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()

        res = r.json()

        # ----- JSON-RPC error handling -------------------------------------
        if err := res.get("error"):
            code = err.get("code", -32000)
            msg  = err.get("message", "Unknown error")
            raise RuntimeError(f"RPC {code}: {msg}")

        result = res["result"]

        # ----- optional pydantic validation --------------------------------
        if out_schema is not None:
            return out_schema.model_validate(result)   # type: ignore[return-value]
        return result

    # context-manager sugar
    def __enter__(self):  return self
    def __exit__(self, *a):  self.close()
    def close(self):  self._client.close() if self._own else None

