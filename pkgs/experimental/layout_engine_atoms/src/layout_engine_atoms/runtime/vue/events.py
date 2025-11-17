from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Literal, Mapping, MutableMapping, Protocol


class SupportsDict(Protocol):
    def dict(self) -> Mapping[str, Any]:
        ...


class EventHandler(Protocol):
    def __call__(
        self, request: Any, payload: Mapping[str, Any] | None = ...
    ) -> Awaitable["UiEventResult | Mapping[str, Any] | None"] | "UiEventResult | Mapping[str, Any] | None":
        ...


def _normalize_payload(payload: Mapping[str, Any] | SupportsDict | None) -> dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, dict):
        return dict(payload)
    if hasattr(payload, "model_dump"):
        return dict(payload.model_dump())
    if hasattr(payload, "dict"):
        return dict(payload.dict())
    return dict(payload)


@dataclass(slots=True)
class UiEventResult:
    """Standardized response payload returned by UI event handlers."""

    body: Mapping[str, Any] | None = None
    channel: str | None = None
    payload: Mapping[str, Any] | None = None
    status_code: int = 200
    headers: Mapping[str, str] | None = None

    def http_body(self) -> dict[str, Any]:
        """Return a JSON-serializable body for the HTTP response."""

        content = _normalize_payload(self.body) if self.body is not None else {}
        if self.channel:
            content.setdefault("channel", self.channel)
        if self.payload is not None:
            content.setdefault("payload", _normalize_payload(self.payload))
        content.setdefault("status", "ok")
        return content


@dataclass(slots=True)
class UiEvent:
    """Declarative description of a frontend-triggered event."""

    id: str
    handler: EventHandler
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "POST"
    description: str | None = None
    payload_schema: Mapping[str, Any] | None = None
    optimistic_response: Mapping[str, Any] | None = None
    default_channel: str | None = None
    meta: MutableMapping[str, Any] = field(default_factory=dict)

    def describe(self) -> dict[str, Any]:
        """Return lightweight metadata consumed by the frontend shell."""

        payload: dict[str, Any] = {
            "id": self.id,
            "method": self.method,
        }
        if self.description:
            payload["description"] = self.description
        if self.payload_schema:
            payload["payloadSchema"] = dict(self.payload_schema)
        if self.optimistic_response:
            payload["optimistic"] = dict(self.optimistic_response)
        if self.default_channel:
            payload["defaultChannel"] = self.default_channel
        if self.meta:
            payload["meta"] = dict(self.meta)
        return payload
