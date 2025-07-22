import json
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

    def model_dump_json(self):
        return json.dumps(self._data)


@pytest.mark.unit
def test_get_request():
    captured = {}

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url, params=params, headers=headers)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"id": 1, "name": "test"})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com")
        result = client.get("/users/1")

    assert captured["url"] == "/users/1"
    assert result == {"id": 1, "name": "test"}


@pytest.mark.unit
def test_get_request_with_params():
    captured = {}

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url, params=params, headers=headers)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"results": []})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com")
        result = client.get("/users", params={"page": 1, "limit": 10})

    assert captured["params"] == {"page": 1, "limit": 10}
    assert result == {"results": []}


@pytest.mark.unit
def test_post_request():
    captured = {}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 2, "name": "new user"})

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com")
        result = client.post(
            "/users", params={"name": "new user", "email": "test@example.com"}
        )

    assert captured["json"] == {"name": "new user", "email": "test@example.com"}
    assert result == {"id": 2, "name": "new user"}


@pytest.mark.unit
def test_put_request():
    captured = {}

    def fake_put(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("PUT", url)
        return httpx.Response(
            200, request=request, json={"id": 1, "name": "updated user"}
        )

    with patch.object(httpx.Client, "put", new=fake_put):
        client = AutoAPIClient("http://example.com")
        result = client.put("/users/1", params={"name": "updated user"})

    assert captured["json"] == {"name": "updated user"}
    assert result == {"id": 1, "name": "updated user"}


@pytest.mark.unit
def test_patch_request():
    captured = {}

    def fake_patch(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("PATCH", url)
        return httpx.Response(
            200, request=request, json={"id": 1, "name": "patched user"}
        )

    with patch.object(httpx.Client, "patch", new=fake_patch):
        client = AutoAPIClient("http://example.com")
        result = client.patch("/users/1", params={"name": "patched user"})

    assert captured["json"] == {"name": "patched user"}
    assert result == {"id": 1, "name": "patched user"}


@pytest.mark.unit
def test_delete_request():
    captured = {}

    def fake_delete(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("DELETE", url)
        return httpx.Response(204, request=request, content=b"")

    with patch.object(httpx.Client, "delete", new=fake_delete):
        client = AutoAPIClient("http://example.com")
        result = client.delete("/users/1")

    assert captured["url"] == "/users/1"
    assert result == {}  # Empty response for 204


@pytest.mark.unit
def test_custom_headers():
    captured = {}

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(headers=headers)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"data": "test"})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com")
        result = client.get(
            "/test", headers={"Authorization": "Bearer token", "Custom": "value"}
        )

    assert "Authorization" in captured["headers"]
    assert captured["headers"]["Authorization"] == "Bearer token"
    assert captured["headers"]["Custom"] == "value"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert result == {"data": "test"}


@pytest.mark.unit
def test_schema_params():
    schema = DummySchema(name="John", email="john@example.com")
    captured = {}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1})

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com")
        result = client.post("/users", params=schema)

    assert captured["json"] == {"name": "John", "email": "john@example.com"}
    assert result == {"id": 1}


@pytest.mark.unit
def test_schema_output():
    def fake_get(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        return httpx.Response(
            200, request=request, json={"name": "John", "email": "john@example.com"}
        )

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com")
        result = client.get("/users/1", out_schema=DummySchema)

    assert isinstance(result, DummySchema)
    assert result._data["name"] == "John"
    assert result._data["email"] == "john@example.com"


@pytest.mark.unit
def test_empty_response_handling():
    def fake_delete(self, url, *, json=None, headers=None):
        request = httpx.Request("DELETE", url)
        return httpx.Response(204, request=request, content=b"")

    with patch.object(httpx.Client, "delete", new=fake_delete):
        client = AutoAPIClient("http://example.com")
        result = client.delete("/users/1")

    assert result == {}


@pytest.mark.unit
def test_text_response_handling():
    def fake_get(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, content=b"plain text response")

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com")
        result = client.get("/text")

    assert result == "plain text response"


@pytest.mark.unit
def test_unsupported_method():
    client = AutoAPIClient("http://example.com")

    with pytest.raises(ValueError, match="Unsupported HTTP method: INVALID"):
        client._make_request("INVALID", "/test")


@pytest.mark.unit
def test_http_error_handling():
    def fake_get(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        response = httpx.Response(404, request=request, json={"error": "Not found"})
        response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Not found", request=request, response=response
            )
        )
        return response

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com")

        with pytest.raises(httpx.HTTPStatusError):
            client.get("/nonexistent")


@pytest.mark.unit
def test_url_none_uses_endpoint():
    captured = {}

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com/api")
        result = client.get()  # No URL provided

    assert captured["url"] == "http://example.com/api"
    assert result == {}


@pytest.mark.unit
def test_url_provided_overrides_endpoint():
    captured = {}

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com/api")
        result = client.get("/custom/path")

    assert captured["url"] == "/custom/path"
    assert result == {}
