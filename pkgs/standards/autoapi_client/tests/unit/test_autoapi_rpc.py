import json
import uuid
from unittest.mock import patch, MagicMock

import httpx
import pytest

from autoapi_client import AutoAPIClient


class DummySchema:
    def __init__(self, **data):
        self._data = data

    @classmethod
    def model_validate(cls, data):
        return cls(**data)

    def model_dump_json(self, **kw):
        data = self._data
        if kw.get("exclude_none"):
            data = {k: v for k, v in data.items() if v is not None}
        return json.dumps(data)


@pytest.mark.unit
def test_rpc_call_basic():
    """Test basic RPC call functionality."""
    captured = {}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json, url=url, headers=headers)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": {"success": True}}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        result = client.call("test.method")

    assert captured["json"]["jsonrpc"] == "2.0"
    assert captured["json"]["method"] == "test.method"
    assert captured["json"]["params"] == {}
    assert "id" in captured["json"]
    assert captured["url"] == "http://example.com/api"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert result == {"success": True}


@pytest.mark.unit
def test_rpc_call_with_dict_params():
    """Test RPC call with dictionary parameters."""
    captured = {}
    params = {"filter": {"name": "test"}, "limit": 10}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": []}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        client.call("list.items", params=params)

    assert captured["json"]["params"] == params


@pytest.mark.unit
def test_rpc_call_with_schema_params():
    """Test RPC call with Pydantic schema parameters."""
    captured = {}
    schema_params = DummySchema(filter={"status": "active"}, page=1, size=20)

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": {"items": []}}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        client.call("search.items", params=schema_params)

    expected_params = {"filter": {"status": "active"}, "page": 1, "size": 20}
    assert captured["json"]["params"] == expected_params


@pytest.mark.unit
def test_rpc_call_with_output_schema():
    """Test RPC call with output schema validation."""

    def fake_post(self, url, *, json=None, headers=None):
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            request=request,
            json={"jsonrpc": "2.0", "result": {"name": "test", "value": 42}},
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        result = client.call("get.item", out_schema=DummySchema)

    assert isinstance(result, DummySchema)
    assert result._data == {"name": "test", "value": 42}


@pytest.mark.unit
def test_rpc_call_error_handling():
    """Test RPC call error handling."""

    def fake_post(self, url, *, json=None, headers=None):
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            request=request,
            json={
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Invalid params"},
            },
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        with pytest.raises(RuntimeError, match="RPC error -32602: Invalid params"):
            client.call("invalid.method")


@pytest.mark.unit
def test_rpc_call_http_error():
    """Test RPC call with HTTP error."""

    def fake_post(self, url, *, json=None, headers=None):
        request = httpx.Request("POST", url)
        response = httpx.Response(500, request=request)
        response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Server Error", request=request, response=response
            )
        )
        return response

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        with pytest.raises(httpx.HTTPStatusError):
            client.call("test.method")


@pytest.mark.unit
def test_rpc_call_filter_params():
    """Test RPC call with complex filter parameters."""
    captured = {}
    filter_params = {
        "filters": {
            "and": [
                {"field": "status", "op": "eq", "value": "active"},
                {"field": "created_at", "op": "gte", "value": "2023-01-01"},
            ]
        },
        "sort": [{"field": "name", "direction": "asc"}],
        "pagination": {"page": 1, "size": 50},
    }

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            request=request,
            json={"jsonrpc": "2.0", "result": {"items": [], "total": 0}},
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        client.call("search.advanced", params=filter_params)

    assert captured["json"]["params"] == filter_params


@pytest.mark.unit
@pytest.mark.parametrize("status_code", [False, True])
@pytest.mark.parametrize("error_code", [False, True])
def test_rpc_call_success_combinations(status_code, error_code):
    """Successful RPC call under various flag combinations."""

    def fake_post(self, url, *, json=None, headers=None):
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": {"ok": True}}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        result = client.call("ping", status_code=status_code, error_code=error_code)

    expected = {"ok": True}
    if status_code and error_code:
        assert result == (expected, 200, None)
    elif status_code:
        assert result == (expected, 200)
    elif error_code:
        assert result == (expected, None)
    else:
        assert result == expected


@pytest.mark.unit
@pytest.mark.parametrize("status_code", [False, True])
@pytest.mark.parametrize("error_code", [False, True])
@pytest.mark.parametrize("raise_status", [True, False])
@pytest.mark.parametrize("raise_error", [True, False])
def test_rpc_call_error_combinations(
    status_code, error_code, raise_status, raise_error
):
    """RPC call flag combinations when both HTTP and RPC errors occur."""

    def fake_post(self, url, *, json=None, headers=None):
        request = httpx.Request("POST", url)
        return httpx.Response(
            500,
            request=request,
            json={"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid"}},
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")

        def call():
            return client.call(
                "bad",
                status_code=status_code,
                error_code=error_code,
                raise_status=raise_status,
                raise_error=raise_error,
            )

        if raise_status:
            with pytest.raises(httpx.HTTPStatusError):
                call()
            return

        if raise_error:
            with pytest.raises(RuntimeError, match="RPC error -32602: Invalid"):
                call()
            return

        result = call()
        expected = [None]
        if status_code:
            expected.append(500)
        if error_code:
            expected.append(-32602)
        assert result == (expected[0] if len(expected) == 1 else tuple(expected))


@pytest.mark.unit
def test_rpc_call_generates_unique_ids():
    """Test that RPC calls generate unique IDs."""
    captured_ids = []

    def fake_post(self, url, *, json=None, headers=None):
        captured_ids.append(json["id"])
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": None}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        client.call("method1")
        client.call("method2")
        client.call("method3")

    # All IDs should be unique and valid UUIDs
    assert len(set(captured_ids)) == 3
    for id_str in captured_ids:
        uuid.UUID(id_str)  # Should not raise exception


@pytest.mark.unit
def test_rpc_call_nested_filter_params():
    """Test RPC call with deeply nested filter parameters."""
    captured = {}
    nested_params = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"status": "published"}},
                    {"range": {"date": {"gte": "2023-01-01", "lte": "2023-12-31"}}},
                ],
                "should": [
                    {"match": {"title": "important"}},
                    {"match": {"tags": "urgent"}},
                ],
                "minimum_should_match": 1,
            }
        },
        "aggregations": {"categories": {"terms": {"field": "category", "size": 10}}},
    }

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            request=request,
            json={"jsonrpc": "2.0", "result": {"hits": [], "aggregations": {}}},
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        client.call("elasticsearch.search", params=nested_params)

    assert captured["json"]["params"] == nested_params
