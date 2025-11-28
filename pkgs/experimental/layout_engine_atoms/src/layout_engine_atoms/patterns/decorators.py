"""Decorators for zero-boilerplate event handling."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable, get_type_hints

from fastapi import Request
from pydantic import BaseModel, ValidationError

from ..runtime.vue import UiEvent, UiEventResult


class EventRegistry:
    """Global registry for decorated event handlers."""

    _handlers: dict[str, UiEvent] = {}

    @classmethod
    def register(cls, event: UiEvent) -> None:
        """Register an event in the global registry."""
        cls._handlers[event.id] = event

    @classmethod
    def get_all(cls) -> list[UiEvent]:
        """Get all registered events."""
        return list(cls._handlers.values())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered events (useful for testing)."""
        cls._handlers.clear()

    @classmethod
    def get(cls, event_id: str) -> UiEvent | None:
        """Get a specific event by ID."""
        return cls._handlers.get(event_id)


def ui_event(
    func: Callable | None = None,
    *,
    event_id: str | None = None,
    channel: str | None = None,
    method: str = "POST",
    description: str | None = None,
) -> Callable:
    """Decorator to automatically register a function as a UiEvent.

    Features:
    - Auto-generates event ID from function name
    - Auto-generates channel name from event ID
    - Extracts description from docstring
    - Auto-validates Pydantic payload models
    - Wraps return values in UiEventResult
    - Registers globally for auto-discovery

    Args:
        func: The function to decorate (when used without parens)
        event_id: Override event ID (default: function name)
        channel: Override channel name (default: "events.{event_id}")
        method: HTTP method (default: "POST")
        description: Override description (default: first line of docstring)

    Example:
        >>> @ui_event
        >>> async def create_user(request: Request, payload: CreateUserPayload):
        ...     '''Create a new user.'''
        ...     user = db.create_user(**payload.model_dump())
        ...     return {"users": db.get_all_users()}

        >>> @ui_event(channel="custom.channel")
        >>> async def custom_handler(request: Request, payload: dict):
        ...     return {"result": "success"}
    """

    def decorator(fn: Callable) -> Callable:
        # Auto-generate event ID from function name
        auto_event_id = event_id or fn.__name__

        # Auto-generate channel name
        auto_channel = channel or f"events.{auto_event_id}"

        # Extract description from docstring if not provided
        auto_description = description or (
            (fn.__doc__ or "").strip().split("\n")[0] if fn.__doc__ else None
        )

        # Get function signature for payload validation
        # Use get_type_hints to resolve string annotations from __future__ imports
        try:
            type_hints = get_type_hints(fn)
        except Exception:
            # Fallback to raw annotations if get_type_hints fails
            type_hints = {}

        sig = inspect.signature(fn)
        params = list(sig.parameters.values())

        # Find payload parameter (second param after request)
        payload_param = params[1] if len(params) > 1 else None
        payload_schema = None
        payload_type = None

        if payload_param and payload_param.name in type_hints:
            payload_type = type_hints[payload_param.name]
            # If it's a Pydantic model, extract schema
            if isinstance(payload_type, type) and issubclass(payload_type, BaseModel):
                payload_schema = payload_type.model_json_schema()

        @wraps(fn)
        async def wrapper(
            request: Request, payload: dict | None = None
        ) -> UiEventResult:
            # Validate and convert payload if Pydantic model is expected
            if (
                payload_type
                and isinstance(payload_type, type)
                and issubclass(payload_type, BaseModel)
            ):
                try:
                    if payload is None:
                        payload = {}
                    validated_payload = payload_type(**payload)
                except ValidationError as e:
                    # Return validation error as event result
                    return UiEventResult(
                        body={"error": "Validation failed", "details": e.errors()},
                        status_code=400,
                    )

                # Call original function with validated model
                result = fn(request, validated_payload)
            else:
                result = fn(request, payload)

            # Handle async
            if inspect.iscoroutine(result):
                result = await result

            # Wrap return value in UiEventResult if needed
            if isinstance(result, UiEventResult):
                return result
            elif isinstance(result, dict):
                return UiEventResult(
                    body=result,
                    channel=auto_channel,
                    payload=result,
                )
            else:
                return UiEventResult(body={"result": result})

        # Create UiEvent
        event = UiEvent(
            id=auto_event_id,
            handler=wrapper,
            method=method,
            description=auto_description,
            payload_schema=payload_schema,
            default_channel=auto_channel,
        )

        # Register globally
        EventRegistry.register(event)

        # Store metadata on wrapper function
        wrapper._ui_event = event  # type: ignore[attr-defined]
        wrapper._event_id = auto_event_id  # type: ignore[attr-defined]
        wrapper._channel = auto_channel  # type: ignore[attr-defined]

        return wrapper

    # Support both @ui_event and @ui_event()
    if func is None:
        return decorator
    else:
        return decorator(func)


def returns_update(*tile_ids: str) -> Callable:
    """Decorator to specify which tiles should receive updates from this handler.

    This is metadata for documentation and potential future auto-binding features.
    Currently serves as clear documentation of event → tile relationships.

    Args:
        *tile_ids: Tile IDs that should be updated when this event fires

    Example:
        >>> @ui_event
        >>> @returns_update("users_table", "user_count_badge")
        >>> async def create_user(request: Request, payload: CreateUserPayload):
        ...     # Handler logic
        ...     return {"users": [...], "count": 42}
    """

    def decorator(fn: Callable) -> Callable:
        # Store metadata on function for introspection
        fn._returns_update_tiles = tile_ids  # type: ignore[attr-defined]
        return fn

    return decorator
