"""Lifecycle contract for HTTP clients that own resources."""

from abc import abstractmethod

from .i_http_client import IHttpClient


class IManagedHttpClient(IHttpClient):
    """HTTP client with explicit synchronous and asynchronous cleanup."""

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    async def aclose(self) -> None:
        pass
