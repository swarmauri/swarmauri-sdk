from __future__ import annotations

from typing import Any

from tigrbl_core._spec.request_spec import RequestSpec


class RequestBase(RequestSpec):
    """Base request model behavior shared by concrete request implementations."""

    @classmethod
    def from_scope(
        cls,
        scope: dict[str, Any],
        receive: Any | None = None,
        *,
        app: Any | None = None,
        state: Any | None = None,
    ) -> "RequestBase":
        """Construct a request from an ASGI scope.

        Middleware/tests may resolve ``Request`` through base/spec surfaces during
        import cycles. Delegate to the concrete request model to keep
        ``Request.from_scope(...)`` consistently available.
        """

        from tigrbl_concrete._concrete._request import Request

        return Request.from_scope(scope, receive, app=app, state=state)


__all__ = ["RequestBase"]
