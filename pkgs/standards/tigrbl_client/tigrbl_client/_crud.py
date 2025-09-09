# tigrbl_client/_crud.py
from __future__ import annotations

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


class CRUDMixin:
    """
    Mixin class providing REST CRUD functionality for TigrblClient.
    """

    def _get_endpoint(self) -> str:
        """Get the endpoint URL."""
        return self._endpoint

    def _get_client(self) -> httpx.Client:
        """Get the HTTP client."""
        return self._client

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get the async HTTP client."""
        return self._async_client

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        if path.startswith("/"):
            return self._get_endpoint() + path
        return f"{self._get_endpoint()}/{path}"

    def _prepare_data(self, data: _Schema[Any] | dict | None) -> dict | None:
        """Prepare data for sending."""
        if data is None:
            return None
        if isinstance(data, _Schema):
            return json.loads(data.model_dump_json(exclude_none=True))
        return data

    def _process_response(
        self,
        response: httpx.Response,
        out_schema: type[_Schema[T]] | None = None,
        *,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """Process HTTP response."""
        if raise_status:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if response.status_code == 422:
                    try:
                        detail = response.json()
                    except ValueError:
                        detail = response.text
                    raise httpx.HTTPStatusError(
                        f"Unprocessable Entity: {detail}",
                        request=exc.request,
                        response=exc.response,
                    ) from None
                raise

        # Handle empty responses (like 204 No Content)
        if response.status_code == 204 or not response.content:
            result: Any = None
        else:
            try:
                result = response.json()
            except ValueError:
                # If response is not JSON, return raw content as string
                result = response.text

        if out_schema is not None and result is not None:
            result = out_schema.model_validate(result)

        if status_code:
            return result, response.status_code
        return result

    # ─────────── GET methods ────────────────────────────────────────── #
    @overload
    def get(
        self,
        path: str,
        *,
        params: dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def get(
        self,
        path: str,
        *,
        params: dict | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def get(
        self,
        path: str,
        *,
        params: dict | None = None,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make a GET request.

        Args:
            path: The path to request (will be appended to endpoint)
            params: Query parameters
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        headers = getattr(self, "_headers", {})
        response = self._get_client().get(url, params=params, headers=headers)
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )

    # ─────────── POST methods ───────────────────────────────────────── #
    @overload
    def post(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def post(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def post(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make a POST request.

        Args:
            path: The path to request (will be appended to endpoint)
            data: Data to send in request body
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        json_data = self._prepare_data(data)
        headers = {"Content-Type": "application/json"}
        headers.update(getattr(self, "_headers", {}))
        response = self._get_client().post(url, json=json_data, headers=headers)
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )

    # ─────────── PUT methods ────────────────────────────────────────── #
    @overload
    def put(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def put(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def put(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make a PUT request.

        Args:
            path: The path to request (will be appended to endpoint)
            data: Data to send in request body
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        json_data = self._prepare_data(data)
        headers = {"Content-Type": "application/json"}
        headers.update(getattr(self, "_headers", {}))
        response = self._get_client().put(url, json=json_data, headers=headers)
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )

    # ─────────── PATCH methods ──────────────────────────────────────── #
    @overload
    def patch(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def patch(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: None = None,
    ) -> Any: ...

    def patch(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make a PATCH request.

        Args:
            path: The path to request (will be appended to endpoint)
            data: Data to send in request body
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        json_data = self._prepare_data(data)
        headers = {"Content-Type": "application/json"}
        headers.update(getattr(self, "_headers", {}))
        response = self._get_client().patch(url, json=json_data, headers=headers)
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )

    # ─────────── DELETE methods ─────────────────────────────────────── #
    @overload
    def delete(
        self,
        path: str,
        *,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    def delete(
        self,
        path: str,
        *,
        out_schema: None = None,
    ) -> Any: ...

    def delete(
        self,
        path: str,
        *,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make a DELETE request.

        Args:
            path: The path to request (will be appended to endpoint)
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        headers = getattr(self, "_headers", {})
        response = self._get_client().delete(url, headers=headers)
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )

    # ─────────── Async GET methods ──────────────────────────────────── #
    @overload
    async def aget(
        self,
        path: str,
        *,
        params: dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def aget(
        self,
        path: str,
        *,
        params: dict | None = None,
        out_schema: None = None,
    ) -> Any: ...

    async def aget(
        self,
        path: str,
        *,
        params: dict | None = None,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make an async GET request.

        Args:
            path: The path to request (will be appended to endpoint)
            params: Query parameters
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        headers = getattr(self, "_headers", {})
        response = await self._get_async_client().get(
            url, params=params, headers=headers
        )
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )

    # ─────────── Async POST methods ─────────────────────────────────── #
    @overload
    async def apost(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def apost(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: None = None,
    ) -> Any: ...

    async def apost(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make an async POST request.

        Args:
            path: The path to request (will be appended to endpoint)
            data: Data to send in request body
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        json_data = self._prepare_data(data)
        headers = {"Content-Type": "application/json"}
        headers.update(getattr(self, "_headers", {}))
        response = await self._get_async_client().post(
            url, json=json_data, headers=headers
        )
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )

    # ─────────── Async PUT methods ──────────────────────────────────── #
    @overload
    async def aput(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def aput(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: None = None,
    ) -> Any: ...

    async def aput(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make an async PUT request.

        Args:
            path: The path to request (will be appended to endpoint)
            data: Data to send in request body
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        json_data = self._prepare_data(data)
        headers = {"Content-Type": "application/json"}
        headers.update(getattr(self, "_headers", {}))
        response = await self._get_async_client().put(
            url, json=json_data, headers=headers
        )
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )

    # ─────────── Async PATCH methods ────────────────────────────────── #
    @overload
    async def apatch(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def apatch(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: None = None,
    ) -> Any: ...

    async def apatch(
        self,
        path: str,
        *,
        data: _Schema[Any] | dict | None = None,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make an async PATCH request.

        Args:
            path: The path to request (will be appended to endpoint)
            data: Data to send in request body
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        json_data = self._prepare_data(data)
        headers = {"Content-Type": "application/json"}
        headers.update(getattr(self, "_headers", {}))
        response = await self._get_async_client().patch(
            url, json=json_data, headers=headers
        )
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )

    # ─────────── Async DELETE methods ──────────────────────────────── #
    @overload
    async def adelete(
        self,
        path: str,
        *,
        out_schema: type[_Schema[T]],
    ) -> T: ...

    @overload
    async def adelete(
        self,
        path: str,
        *,
        out_schema: None = None,
    ) -> Any: ...

    async def adelete(
        self,
        path: str,
        *,
        out_schema: type[_Schema[T]] | None = None,
        status_code: bool = False,
        raise_status: bool = True,
    ) -> Any:
        """
        Make an async DELETE request.

        Args:
            path: The path to request (will be appended to endpoint)
            out_schema: Optional Pydantic schema for response validation

        Returns:
            The response data, optionally validated through out_schema
        """
        url = self._build_url(path)
        headers = getattr(self, "_headers", {})
        response = await self._get_async_client().delete(url, headers=headers)
        return self._process_response(
            response, out_schema, status_code=status_code, raise_status=raise_status
        )
