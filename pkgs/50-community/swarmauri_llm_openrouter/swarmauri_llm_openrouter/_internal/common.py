"""Share OpenRouter payload, response, and event helpers."""

import json
from typing import Any

from swarmauri_standard.messages.AgentMessage import AgentMessage, UsageData


def format_messages(messages: list[Any]) -> list[dict[str, Any]]:
    """Convert Swarmauri messages without flattening multimodal content."""
    return [
        message.model_dump(
            include={"content", "role", "name", "tool_calls", "tool_call_id"},
            exclude_none=True,
        )
        for message in messages
    ]


def compact(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove only unset request values while preserving false and zero."""
    return {key: value for key, value in payload.items() if value is not None}


def add_assistant_response(conversation: Any, response: dict[str, Any]) -> Any:
    """Append a normalized OpenRouter assistant response to a conversation."""
    message = response["choices"][0]["message"]
    usage_data = response.get("usage")
    conversation.add_message(
        AgentMessage(
            content=message.get("content"),
            tool_calls=message.get("tool_calls"),
            usage=UsageData.model_validate(usage_data) if usage_data else None,
        )
    )
    return conversation


def delta_text(event: dict[str, Any]) -> str | None:
    """Return text content from a normalized streaming event."""
    choices = event.get("choices") or []
    if not choices:
        return None
    return choices[0].get("delta", {}).get("content")


def decode_sse_line(line: str) -> dict[str, Any] | None:
    """Decode one OpenRouter server-sent event without owning I/O."""
    if not line or line.startswith(":") or not line.startswith("data:"):
        return None
    data = line[5:].strip()
    if not data or data == "[DONE]":
        return None
    return json.loads(data)
