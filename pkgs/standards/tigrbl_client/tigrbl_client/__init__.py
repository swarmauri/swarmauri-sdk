# tigrbl_client/__init__.py
from __future__ import annotations

import httpx
from typing import TypeVar

from ._rpc import RPCMixin, _Schema
from ._crud import CRUDMixin
from ._nested_crud import NestedCRUDMixin

T = TypeVar("T")


# Re-export the Schema protocol for public use
__all__ = ["TigrblClient", "_Schema"]


class TigrblClient(RPCMixin, CRUDMixin, NestedCRUDMixin):
    """
    Unified API client supporting both JSON-RPC and REST CRUD operations.

    Features:
    * JSON-RPC calls with optional Pydantic schema validation
    * REST CRUD operations (GET, POST, PUT, PATCH, DELETE)
    * Async versions of all operations (aget, apost, aput, apatch, adelete)
    * Connection pooling via httpx.Client
    * Optional Pydantic schema validation for requests and responses
    * Placeholder for future nested CRUD operations
    * Works with Tigrbl services that expose operations via resource-based
      namespaces (e.g., ``api.core.Users.create`` or ``api.rpc.Users.login``)

    Examples:
        # JSON-RPC usage
        client = TigrblClient("http://api.example.com/rpc")
        result = client.call("user.get", params={"id": 123})

        # REST CRUD usage
        client = TigrblClient("http://api.example.com")
        user = client.get("/users/123")
        new_user = client.post("/users", data={"name": "John", "email": "john@example.com"})

        # Async usage
        user = await client.aget("/users/123")
        result = await client.apost("/users", data={"name": "Jane"})
    """

    def __init__(
        self,
        endpoint: str,
        *,
        client: httpx.Client | None = None,
        headers: dict[str, str] | None = None,
        api_key: str | None = None,
    ) -> None:
        """
        Initialize the TigrblClient.

        Args:
            endpoint: Base URL for the API
            client: Optional httpx.Client instance. If not provided, a new one will be created.
            headers: Optional default headers for all requests.
            api_key: Optional API key for authenticated requests. The key is
                sent using the ``x-api-key`` header.
        """
        self._endpoint = endpoint
        self._own = client is None  # whether we manage its lifecycle
        self._client = client or httpx.Client(timeout=10.0)
        self._headers = headers.copy() if headers else {}
        self.api_key = api_key

        # Create async client for async operations
        self._async_client = httpx.AsyncClient(timeout=10.0)
        self._own_async = True  # we always own the async client

        # Initialize nested CRUD placeholder
        NestedCRUDMixin.__init__(self)

    @property
    def api_key(self) -> str | None:
        """Return the currently configured API key, if any."""
        return self._headers.get("x-api-key")

    @api_key.setter
    def api_key(self, value: str | None) -> None:
        """Set or remove the API key used for requests."""
        if value is None:
            self._headers.pop("x-api-key", None)
        else:
            self._headers["x-api-key"] = value

    def _get_endpoint(self) -> str:
        """Get the endpoint URL."""
        return self._endpoint

    def _get_client(self) -> httpx.Client:
        """Get the HTTP client."""
        return self._client

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get the async HTTP client."""
        return self._async_client

    # Context manager support
    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, *args):
        """Exit context manager."""
        self.close()

    async def __aenter__(self):
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args):
        """Exit async context manager."""
        await self.aclose()

    def close(self):
        """Close the HTTP clients."""
        if self._own:
            self._client.close()

    async def aclose(self):
        """Close the async HTTP client."""
        if self._own_async:
            await self._async_client.aclose()
