"""
Error Mappings and Parity Tests for AutoAPI v2

Tests error mappings between RPC and HTTP, and verifies parity between error responses.
"""

import pytest
from autoapi.v2.jsonrpc_models import (
    _HTTP_TO_RPC,
    _RPC_TO_HTTP,
    ERROR_MESSAGES,
    HTTP_ERROR_MESSAGES,
    _http_exc_to_rpc,
    _rpc_error_to_http,
    create_standardized_error,
)
from fastapi import HTTPException


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_http_to_rpc_error_mapping():
    """Test that HTTP status codes map correctly to RPC error codes."""
    # Test known mappings from _HTTP_TO_RPC
    test_cases = [
        (400, -32602),  # Bad Request -> Invalid params
        (401, -32001),  # Unauthorized -> Authentication required
        (403, -32002),  # Forbidden -> Insufficient permissions
        (404, -32003),  # Not Found -> Resource not found
        (409, -32004),  # Conflict -> Resource conflict
        (422, -32602),  # Unprocessable Entity -> Invalid params
        (500, -32603),  # Internal Server Error -> Internal error
    ]

    for http_code, expected_rpc_code in test_cases:
        assert _HTTP_TO_RPC[http_code] == expected_rpc_code


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rpc_to_http_error_mapping():
    """Test that RPC error codes map correctly to HTTP status codes."""
    # Test known mappings from _RPC_TO_HTTP
    test_cases = [
        (-32700, 400),  # Parse error -> Bad Request
        (-32600, 400),  # Invalid Request -> Bad Request
        (-32601, 404),  # Method not found -> Not Found
        (-32602, 400),  # Invalid params -> Bad Request
        (-32603, 500),  # Internal error -> Internal Server Error
        (-32001, 401),  # Authentication required -> Unauthorized
        (-32002, 403),  # Insufficient permissions -> Forbidden
        (-32003, 404),  # Resource not found -> Not Found
        (-32004, 409),  # Resource conflict -> Conflict
    ]

    for rpc_code, expected_http_code in test_cases:
        assert _RPC_TO_HTTP[rpc_code] == expected_http_code


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_error_message_standardization():
    """Test that error messages are standardized and consistent."""
    # Test that ERROR_MESSAGES contains expected keys
    expected_rpc_codes = [
        -32700,
        -32600,
        -32601,
        -32602,
        -32603,
        -32001,
        -32002,
        -32003,
        -32004,
    ]

    for code in expected_rpc_codes:
        assert code in ERROR_MESSAGES
        assert isinstance(ERROR_MESSAGES[code], str)
        assert len(ERROR_MESSAGES[code]) > 0

    # Test that HTTP_ERROR_MESSAGES contains expected keys
    expected_http_codes = [400, 401, 403, 404, 409, 422, 500]

    for code in expected_http_codes:
        assert code in HTTP_ERROR_MESSAGES
        assert isinstance(HTTP_ERROR_MESSAGES[code], str)
        assert len(HTTP_ERROR_MESSAGES[code]) > 0


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_http_exc_to_rpc_conversion():
    """Test conversion from HTTP exceptions to RPC errors."""
    # Test with standard HTTP exception
    http_exc = HTTPException(status_code=404, detail="Resource not found")
    rpc_code, rpc_message = _http_exc_to_rpc(http_exc)

    assert rpc_code == -32003  # Resource not found
    assert rpc_message == "Resource not found"

    # Test with HTTP exception that has custom message
    http_exc = HTTPException(status_code=400, detail="Custom bad request message")
    rpc_code, rpc_message = _http_exc_to_rpc(http_exc)

    assert rpc_code == -32602  # Invalid params
    assert rpc_message == "Custom bad request message"

    # Test with unmapped HTTP status code (should default to internal error)
    http_exc = HTTPException(status_code=418, detail="I'm a teapot")
    rpc_code, rpc_message = _http_exc_to_rpc(http_exc)

    assert rpc_code == -32603  # Internal error
    assert rpc_message == "I'm a teapot"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rpc_error_to_http_conversion():
    """Test conversion from RPC errors to HTTP exceptions."""
    # Test with standard RPC error
    http_exc = _rpc_error_to_http(-32003, "Resource not found")

    assert http_exc.status_code == 404
    assert http_exc.detail == "Resource not found"

    # Test with RPC error without custom message (should use default)
    http_exc = _rpc_error_to_http(-32001)

    assert http_exc.status_code == 401
    assert http_exc.detail == HTTP_ERROR_MESSAGES[401]

    # Test with unmapped RPC error code (should default to 500)
    http_exc = _rpc_error_to_http(-99999, "Unknown error")

    assert http_exc.status_code == 500
    assert http_exc.detail == "Unknown error"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_create_standardized_error():
    """Test creation of standardized errors."""
    # Test creating error from HTTP status
    http_exc, rpc_code, rpc_message = create_standardized_error(404, "Custom not found")

    assert http_exc.status_code == 404
    assert http_exc.detail == "Custom not found"
    assert rpc_code == -32003
    assert rpc_message == "Custom not found"

    # Test creating error with explicit RPC code
    http_exc, rpc_code, rpc_message = create_standardized_error(
        400, "Bad request", -32602
    )

    assert http_exc.status_code == 400
    assert http_exc.detail == "Bad request"
    assert rpc_code == -32602
    assert rpc_message == "Bad request"

    # Test creating error with default message
    http_exc, rpc_code, rpc_message = create_standardized_error(401)

    assert http_exc.status_code == 401
    assert http_exc.detail == HTTP_ERROR_MESSAGES[401]
    assert rpc_code == -32001
    assert rpc_message == ERROR_MESSAGES[-32001]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_error_parity_crud_vs_rpc(api_client):
    """Test that CRUD and RPC operations return equivalent errors."""
    client, api, _ = api_client

    # Test 404 error parity
    # Try to read non-existent item via REST
    rest_response = await client.get("/items/00000000-0000-0000-0000-000000000000")
    assert rest_response.status_code == 404
    rest_error = rest_response.json()

    # Try to read non-existent item via RPC
    rpc_response = await client.post(
        "/rpc",
        json={
            "method": "Items.read",
            "params": {"id": "00000000-0000-0000-0000-000000000000"},
        },
    )
    assert rpc_response.status_code == 200  # RPC always returns 200
    rpc_data = rpc_response.json()
    assert "error" in rpc_data
    rpc_error = rpc_data["error"]

    # Both should indicate the same type of error
    assert rpc_error["code"] == -32003  # Resource not found
    # The messages should be equivalent in meaning
    assert "not found" in rest_error["detail"].lower()
    assert "not found" in rpc_error["message"].lower()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_error_parity_validation_errors(api_client):
    """Test that validation errors are consistent between CRUD and RPC."""
    client, api, _ = api_client

    # Test validation error - missing required field
    # Try via REST
    rest_response = await client.post("/tenants", json={})  # Missing name
    assert rest_response.status_code == 422
    rest_error = rest_response.json()

    # Try via RPC
    rpc_response = await client.post(
        "/rpc",
        json={"method": "Tenants.create", "params": {}},  # Missing name
    )
    assert rpc_response.status_code == 200
    rpc_data = rpc_response.json()
    assert "error" in rpc_data
    rpc_error = rpc_data["error"]

    # Both should indicate validation error
    assert rpc_error["code"] == -32602  # Invalid params
    # Both should mention the validation issue
    assert "name" in str(rest_error).lower()
    assert "name" in rpc_error["message"].lower()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_error_mapping_bidirectional_consistency():
    """Test that error mappings are bidirectionally consistent."""
    # For each HTTP->RPC mapping, verify the reverse RPC->HTTP mapping exists
    for http_code, rpc_code in _HTTP_TO_RPC.items():
        assert rpc_code in _RPC_TO_HTTP
        # The reverse mapping should map back to a reasonable HTTP code
        reverse_http_code = _RPC_TO_HTTP[rpc_code]
        # It doesn't have to be exactly the same (e.g., 422 and 400 both map to -32602)
        # But it should be in the same error class
        assert reverse_http_code // 100 == http_code // 100 or (
            http_code in [400, 422] and reverse_http_code in [400, 422]
        )


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_error_response_structure(api_client):
    """Test that error responses have consistent structure."""
    client, api, _ = api_client

    # Test REST error structure
    rest_response = await client.get("/items/invalid-uuid")
    rest_error = rest_response.json()

    # REST errors should have detail field
    assert "detail" in rest_error

    # Test RPC error structure
    rpc_response = await client.post(
        "/rpc", json={"method": "Items.read", "params": {"id": "invalid-uuid"}}
    )
    rpc_data = rpc_response.json()

    if "error" in rpc_data:
        rpc_error = rpc_data["error"]

        # RPC errors should have code and message
        assert "code" in rpc_error
        assert "message" in rpc_error
        assert isinstance(rpc_error["code"], int)
        assert isinstance(rpc_error["message"], str)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_custom_error_messages_preserved():
    """Test that custom error messages are preserved through conversions."""
    custom_message = "This is a custom error message for testing"

    # Test HTTP to RPC conversion preserves message
    http_exc = HTTPException(status_code=404, detail=custom_message)
    rpc_code, rpc_message = _http_exc_to_rpc(http_exc)
    assert rpc_message == custom_message

    # Test RPC to HTTP conversion preserves message
    http_exc = _rpc_error_to_http(-32003, custom_message)
    assert http_exc.detail == custom_message

    # Test standardized error creation preserves message
    http_exc, rpc_code, rpc_message = create_standardized_error(404, custom_message)
    assert http_exc.detail == custom_message
    assert rpc_message == custom_message


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_error_mapping_completeness():
    """Test that error mappings cover all expected scenarios."""
    # Common HTTP error codes should be mapped
    common_http_codes = [400, 401, 403, 404, 409, 422, 500, 503]

    for code in common_http_codes:
        if code in _HTTP_TO_RPC:
            # If mapped, should have corresponding RPC code
            rpc_code = _HTTP_TO_RPC[code]
            assert rpc_code in _RPC_TO_HTTP
            assert rpc_code in ERROR_MESSAGES

        # Should have HTTP error message
        if code in HTTP_ERROR_MESSAGES:
            assert isinstance(HTTP_ERROR_MESSAGES[code], str)
            assert len(HTTP_ERROR_MESSAGES[code]) > 0

    # Common RPC error codes should be mapped
    common_rpc_codes = [
        -32700,
        -32600,
        -32601,
        -32602,
        -32603,
        -32001,
        -32002,
        -32003,
        -32004,
    ]

    for code in common_rpc_codes:
        assert code in _RPC_TO_HTTP
        assert code in ERROR_MESSAGES

        # Should map to valid HTTP code
        http_code = _RPC_TO_HTTP[code]
        assert 400 <= http_code <= 599
