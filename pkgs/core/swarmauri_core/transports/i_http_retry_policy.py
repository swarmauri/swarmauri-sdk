"""Decision contract for concrete HTTP retry policies."""

from abc import ABC, abstractmethod

from .i_http_response import IHttpResponse


class IHttpRetryPolicy(ABC):
    """Decide whether and when an HTTP operation may be retried."""

    @abstractmethod
    def should_retry(
        self,
        *,
        method: str,
        attempt: int,
        response: IHttpResponse | None = None,
        error: Exception | None = None,
    ) -> bool:
        pass

    @abstractmethod
    def delay_seconds(
        self,
        *,
        attempt: int,
        response: IHttpResponse | None = None,
    ) -> float:
        pass
