"""Tests for security features in the Vue runtime."""

from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI, Request, WebSocket
from fastapi.testclient import TestClient

from layout_engine_atoms.runtime.vue import (
    LayoutOptions,
    RealtimeOptions,
    UiEvent,
    UiEventResult,
    mount_layout_app,
)
from layout_engine_atoms.runtime.vue.validation import (
    PayloadValidationError,
    validate_client_setup_code,
    validate_payload_against_schema,
)


def test_payload_validation_with_schema():
    """Test payload validation against JSON schema."""
    schema = {
        "type": "object",
        "required": ["name", "age"],
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
        },
    }

    # Valid payload
    valid_payload = {"name": "John", "age": 30}
    validate_payload_against_schema(valid_payload, schema)  # Should not raise

    # Missing required field
    with pytest.raises(PayloadValidationError, match="Missing required fields"):
        validate_payload_against_schema({"name": "John"}, schema)

    # Wrong type
    with pytest.raises(PayloadValidationError, match="expected integer"):
        validate_payload_against_schema({"name": "John", "age": "thirty"}, schema)

    # Out of range
    with pytest.raises(PayloadValidationError, match="value above maximum"):
        validate_payload_against_schema({"name": "John", "age": 200}, schema)


def test_xss_protection_in_client_setup():
    """Test that dangerous patterns are detected in client_setup."""
    # Script tags should be rejected
    with pytest.raises(ValueError, match="potentially dangerous pattern"):
        validate_client_setup_code("<script>alert('xss')</script>")

    # Event handlers should be rejected
    with pytest.raises(ValueError, match="potentially dangerous pattern"):
        validate_client_setup_code('onload="alert(\'xss\')"')

    # javascript: protocol should be rejected
    with pytest.raises(ValueError, match="potentially dangerous pattern"):
        validate_client_setup_code("javascript:alert('xss')")

    # eval should be rejected
    with pytest.raises(ValueError, match="potentially dangerous pattern"):
        validate_client_setup_code("eval('malicious code')")

    # Safe code should pass
    safe_code = """
    console.log('Dashboard initialized');
    context.manifest.tiles.forEach(tile => {
        console.log(tile.id);
    });
    """
    validate_client_setup_code(safe_code)  # Should not raise


def test_event_payload_validation_integration():
    """Test that event payloads are validated in the API."""
    app = FastAPI()

    async def test_handler(request: Request, payload: dict | None = None):
        return UiEventResult(body={"received": payload})

    def manifest_builder(request: Request):
        return {"kind": "LayoutManifest", "tiles": []}

    # Mount with validation schema
    mount_layout_app(
        app,
        manifest_builder,
        events=[
            UiEvent(
                id="test.event",
                handler=test_handler,
                payload_schema={
                    "type": "object",
                    "required": ["value"],
                    "properties": {"value": {"type": "integer"}},
                },
            )
        ],
    )

    client = TestClient(app)

    # Valid payload should succeed
    response = client.post("/dashboard/events/test.event", json={"value": 42})
    assert response.status_code == 200

    # Missing required field should fail
    response = client.post("/dashboard/events/test.event", json={})
    assert response.status_code == 400
    assert "Missing required fields" in response.json()["detail"]

    # Wrong type should fail
    response = client.post("/dashboard/events/test.event", json={"value": "string"})
    assert response.status_code == 400
    assert "expected integer" in response.json()["detail"]


def test_client_setup_validation_in_mount():
    """Test that client_setup is validated when mounting."""
    app = FastAPI()

    def manifest_builder(request: Request):
        return {"kind": "LayoutManifest", "tiles": []}

    # Safe client_setup should work
    from layout_engine_atoms.runtime.vue import UIHooks

    mount_layout_app(
        app,
        manifest_builder,
        ui_hooks=UIHooks(client_setup="console.log('Hello');"),
    )

    # Dangerous client_setup should raise
    app2 = FastAPI()
    with pytest.raises(ValueError, match="Security validation failed"):
        mount_layout_app(
            app2,
            manifest_builder,
            ui_hooks=UIHooks(client_setup="<script>alert('xss')</script>"),
        )


@pytest.mark.asyncio
async def test_websocket_authentication():
    """Test WebSocket authentication."""
    app = FastAPI()

    async def auth_handler(websocket: WebSocket) -> bool:
        # Check for auth token in query params
        token = websocket.query_params.get("token")
        return token == "valid_token"

    def manifest_builder(request: Request):
        return {"kind": "LayoutManifest", "tiles": []}

    mount_layout_app(
        app,
        manifest_builder,
        realtime=RealtimeOptions(
            path="/ws/events",
            channels=[],
            auth_handler=auth_handler,
        ),
    )

    # Test with valid token (would require actual WebSocket testing)
    # This is a placeholder - actual WebSocket auth testing requires
    # more complex setup with test WebSocket clients


def test_rate_limiting_enabled():
    """Test that rate limiting works when enabled."""
    app = FastAPI()

    async def test_handler(request: Request, payload: dict | None = None):
        return UiEventResult(body={"success": True})

    def manifest_builder(request: Request):
        return {"kind": "LayoutManifest", "tiles": []}

    # Enable rate limiting with low limit for testing
    mount_layout_app(
        app,
        manifest_builder,
        layout_options=LayoutOptions(
            enable_rate_limiting=True,
            rate_limit_requests=5,  # Only 5 requests allowed
            rate_limit_window=60,  # per 60 seconds
        ),
        events=[UiEvent(id="test.event", handler=test_handler)],
    )

    client = TestClient(app)

    # First 5 requests should succeed
    for i in range(5):
        response = client.post("/dashboard/events/test.event", json={})
        assert response.status_code == 200, f"Request {i+1} failed"

    # 6th request should be rate limited
    response = client.post("/dashboard/events/test.event", json={})
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
    assert "Retry-After" in response.headers


def test_rate_limiting_disabled_by_default():
    """Test that rate limiting is disabled by default."""
    app = FastAPI()

    async def test_handler(request: Request, payload: dict | None = None):
        return UiEventResult(body={"success": True})

    def manifest_builder(request: Request):
        return {"kind": "LayoutManifest", "tiles": []}

    mount_layout_app(
        app,
        manifest_builder,
        events=[UiEvent(id="test.event", handler=test_handler)],
    )

    client = TestClient(app)

    # Should be able to make many requests without rate limiting
    for _ in range(100):
        response = client.post("/dashboard/events/test.event", json={})
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_websocket_subscription_limit():
    """Test that WebSocket subscriptions are limited."""
    from layout_engine_atoms.runtime.vue.realtime import (
        RealtimeChannel,
        WebsocketMuxHub,
    )

    hub = WebsocketMuxHub(path="/ws/events", max_subscriptions_per_client=3)

    # Create mock websocket
    class MockWebSocket:
        def __init__(self):
            self.client = type("Client", (), {"host": "127.0.0.1"})()
            self.accepted = False

        async def accept(self):
            self.accepted = True

        async def send_json(self, data):
            pass

    ws = MockWebSocket()
    await hub.connect(ws)

    # Should be able to subscribe to 3 channels
    await hub.subscribe(ws, "channel1")
    await hub.subscribe(ws, "channel2")
    await hub.subscribe(ws, "channel3")

    # 4th subscription should be rejected (no error raised, but error sent to client)
    await hub.subscribe(ws, "channel4")

    # Verify only 3 channels are subscribed
    assert len(hub._subscriptions[ws]) == 3


def test_invalid_json_payload_handling():
    """Test that invalid JSON payloads are properly handled."""
    app = FastAPI()

    async def test_handler(request: Request, payload: dict | None = None):
        return UiEventResult(body={"received": payload})

    def manifest_builder(request: Request):
        return {"kind": "LayoutManifest", "tiles": []}

    mount_layout_app(
        app,
        manifest_builder,
        events=[UiEvent(id="test.event", handler=test_handler)],
    )

    client = TestClient(app)

    # Send invalid JSON
    response = client.post(
        "/dashboard/events/test.event",
        data="not valid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert "Invalid JSON payload" in response.json()["detail"]


@pytest.mark.asyncio
async def test_rate_limiter_cleanup():
    """Test that rate limiter cleanup works."""
    from layout_engine_atoms.runtime.vue.rate_limit import InMemoryRateLimiter

    limiter = InMemoryRateLimiter(max_requests=10, window_seconds=1)
    limiter.start_cleanup()

    # Give cleanup task time to start
    await asyncio.sleep(0.1)

    # Stop cleanup
    await limiter.stop_cleanup()

    # Cleanup task should be None after stopping
    assert limiter._cleanup_task is None


def test_payload_validation_with_enum():
    """Test payload validation with enum constraints."""
    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["pending", "active", "completed"]},
        },
    }

    # Valid enum value
    validate_payload_against_schema({"status": "active"}, schema)

    # Invalid enum value
    with pytest.raises(PayloadValidationError, match="must be one of"):
        validate_payload_against_schema({"status": "invalid"}, schema)


def test_payload_validation_with_string_length():
    """Test payload validation with string length constraints."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 3, "maxLength": 10},
        },
    }

    # Valid length
    validate_payload_against_schema({"name": "John"}, schema)

    # Too short
    with pytest.raises(PayloadValidationError, match="string too short"):
        validate_payload_against_schema({"name": "ab"}, schema)

    # Too long
    with pytest.raises(PayloadValidationError, match="string too long"):
        validate_payload_against_schema({"name": "verylongname"}, schema)
