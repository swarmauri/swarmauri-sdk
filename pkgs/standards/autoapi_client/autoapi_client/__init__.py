# autoapi_client/__init__.py
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


# --------------------------------------------------------------------- #
class AutoAPIClient:
    """
    Tiny, dependency-free HTTP client for AutoAPI.
    * Uses httpx for async / sync requests.
    * Supports GET, POST, PUT, PATCH, DELETE methods.
    * Generates ids, sets Content-Type, decodes error envelopes.
    * Optional pydantic schema validation on both params & result.
    * Backward compatible JSON-RPC interface.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ):
        self._endpoint = endpoint
        self._own_sync = client is None
        self._own_async = async_client is None
        self._client = client or httpx.Client(timeout=10.0)
        self._async_client = async_client

    # ─────────── JSON-RPC backward compatibility ───────────────────── #
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
        """Legacy JSON-RPC call method for backward compatibility."""
        # ----- payload build ------------------------------------------------
        if isinstance(params, _Schema):  # pydantic in → dump to dict
            params_dict = json.loads(params.model_dump_json())
        else:
            params_dict = params or {}

        req = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params_dict,
            "id": str(uuid.uuid4()),
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
            msg = err.get("message", "Unknown error")
            raise RuntimeError(f"RPC {code}: {msg}")

        result = res["result"]

        # ----- optional pydantic validation --------------------------------
        if out_schema is not None:
            return out_schema.model_validate(result)  # type: ignore[return-value]
        return result

    # ─────────── HTTP method helpers - Sync ───────────────────────── #
    def _make_request(
        self,
        method: str,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]] | None = None,
    ) -> Any:
        """Internal method to make HTTP requests with optional schema validation."""
        target_url = url or self._endpoint

        # Prepare request data
        request_data = None
        if params:
            if isinstance(params, _Schema):
                request_data = json.loads(params.model_dump_json())
            else:
                request_data = params

        # Set default headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)

        # Make the request
        if method.upper() == "GET":
            r = self._client.get(target_url, params=request_data, headers=req_headers)
        elif method.upper() == "POST":
            r = self._client.post(target_url, json=request_data, headers=req_headers)
        elif method.upper() == "PUT":
            r = self._client.put(target_url, json=request_data, headers=req_headers)
        elif method.upper() == "PATCH":
            r = self._client.patch(target_url, json=request_data, headers=req_headers)
        elif method.upper() == "DELETE":
            r = self._client.delete(target_url, json=request_data, headers=req_headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        r.raise_for_status()

        # Handle empty responses
        try:
            result = r.json() if r.content else {}
        except json.JSONDecodeError:
            result = r.text if r.text else None

        # Optional schema validation
        if out_schema is not None and result is not None:
            return out_schema.model_validate(result)  # type: ignore[return-value]
        return result

    @overload
    def get(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def get(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def get(self, url: str | None = None, **kwargs) -> Any:
        """Make a GET request."""
        return self._make_request("GET", url, **kwargs)

    @overload
    def post(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def post(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def post(self, url: str | None = None, **kwargs) -> Any:
        """Make a POST request."""
        return self._make_request("POST", url, **kwargs)

    @overload
    def put(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def put(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def put(self, url: str | None = None, **kwargs) -> Any:
        """Make a PUT request."""
        return self._make_request("PUT", url, **kwargs)

    @overload
    def patch(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def patch(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def patch(self, url: str | None = None, **kwargs) -> Any:
        """Make a PATCH request."""
        return self._make_request("PATCH", url, **kwargs)

    @overload
    def delete(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def delete(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def delete(self, url: str | None = None, **kwargs) -> Any:
        """Make a DELETE request."""
        return self._make_request("DELETE", url, **kwargs)

    # ─────────── HTTP method helpers - Async ──────────────────────── #
    async def _amake_request(
        self,
        method: str,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]] | None = None,
    ) -> Any:
        """Internal async method to make HTTP requests with optional schema validation."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=10.0)
            self._own_async = True

        target_url = url or self._endpoint

        # Prepare request data
        request_data = None
        if params:
            if isinstance(params, _Schema):
                request_data = json.loads(params.model_dump_json())
            else:
                request_data = params

        # Set default headers
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)

        # Make the request
        if method.upper() == "GET":
            r = await self._async_client.get(
                target_url, params=request_data, headers=req_headers
            )
        elif method.upper() == "POST":
            r = await self._async_client.post(
                target_url, json=request_data, headers=req_headers
            )
        elif method.upper() == "PUT":
            r = await self._async_client.put(
                target_url, json=request_data, headers=req_headers
            )
        elif method.upper() == "PATCH":
            r = await self._async_client.patch(
                target_url, json=request_data, headers=req_headers
            )
        elif method.upper() == "DELETE":
            r = await self._async_client.delete(
                target_url, json=request_data, headers=req_headers
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        r.raise_for_status()

        # Handle empty responses
        try:
            result = r.json() if r.content else {}
        except json.JSONDecodeError:
            result = r.text if r.text else None

        # Optional schema validation
        if out_schema is not None and result is not None:
            return out_schema.model_validate(result)  # type: ignore[return-value]
        return result

    @overload
    async def aget(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def aget(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    async def aget(self, url: str | None = None, **kwargs) -> Any:
        """Make an async GET request."""
        return await self._amake_request("GET", url, **kwargs)

    @overload
    async def apost(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def apost(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    async def apost(self, url: str | None = None, **kwargs) -> Any:
        """Make an async POST request."""
        return await self._amake_request("POST", url, **kwargs)

    @overload
    async def aput(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def aput(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    async def aput(self, url: str | None = None, **kwargs) -> Any:
        """Make an async PUT request."""
        return await self._amake_request("PUT", url, **kwargs)

    @overload
    async def apatch(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def apatch(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    async def apatch(self, url: str | None = None, **kwargs) -> Any:
        """Make an async PATCH request."""
        return await self._amake_request("PATCH", url, **kwargs)

    @overload
    async def adelete(
        self,
        url: str | None = None,
        *,
        params: _Schema[Any] | dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def adelete(
        self,
        url: str | None = None,
        *,
        params: dict | None = None,
        headers: dict[str, str] | None = None,
        out_schema: None = None,
    ) -> Any: ...

    async def adelete(self, url: str | None = None, **kwargs) -> Any:
        """Make an async DELETE request."""
        return await self._amake_request("DELETE", url, **kwargs)

    # ─────────── Context manager and cleanup ──────────────────────── #
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        await self.aclose()

    def close(self):
        """Close the synchronous client if we own it."""
        if self._own_sync:
            self._client.close()

    async def aclose(self):
        """Close the asynchronous client if we own it."""
        if self._own_async and self._async_client:
            await self._async_client.aclose()
