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

    def model_dump_json(self, **kw):
        data = self._data
        if kw.get("exclude_none"):
            data = {k: v for k, v in data.items() if v is not None}
        return json.dumps(data)


# Async GET Tests
@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_basic():
    """Test basic async GET request functionality."""
    captured = {}

    async def fake_aget(self, url, *, params=None, headers=None):
        captured.update(url=url, params=params, headers=headers)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"id": 1, "name": "test"})

    with patch.object(httpx.AsyncClient, "get", new=fake_aget):
        client = AutoAPIClient("http://example.com/api")
        result = await client.aget("/users/1")

    assert captured["url"] == "http://example.com/api/users/1"
    assert result == {"id": 1, "name": "test"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_with_params():
    """Test async GET request with query parameters."""
    captured = {}

    async def fake_aget(self, url, *, params=None, headers=None):
        captured.update(url=url, params=params)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"items": [], "total": 0})

    with patch.object(httpx.AsyncClient, "get", new=fake_aget):
        client = AutoAPIClient("http://example.com/api")
        await client.aget("/users", params={"page": 1, "limit": 10, "status": "active"})

    assert captured["params"] == {"page": 1, "limit": 10, "status": "active"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_with_schema():
    """Test async GET request with output schema validation."""

    async def fake_aget(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"name": "test", "value": 42})

    with patch.object(httpx.AsyncClient, "get", new=fake_aget):
        client = AutoAPIClient("http://example.com/api")
        result = await client.aget("/items/1", out_schema=DummySchema)

    assert isinstance(result, DummySchema)
    assert result._data == {"name": "test", "value": 42}


# Async POST Tests
@pytest.mark.unit
@pytest.mark.asyncio
async def test_apost_basic():
    """Test basic async POST request functionality."""
    captured = {}
    data = {"name": "New User", "email": "user@example.com"}

    async def fake_apost(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1, **data})

    with patch.object(httpx.AsyncClient, "post", new=fake_apost):
        client = AutoAPIClient("http://example.com/api")
        result = await client.apost("/users", data=data)

    assert captured["url"] == "http://example.com/api/users"
    assert captured["json"] == data
    assert captured["headers"]["Content-Type"] == "application/json"
    assert result == {"id": 1, **data}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apost_with_schema_data():
    """Test async POST request with Pydantic schema data."""
    captured = {}
    schema_data = DummySchema(name="Test User", email="test@example.com", age=25)

    async def fake_apost(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1, "status": "created"})

    with patch.object(httpx.AsyncClient, "post", new=fake_apost):
        client = AutoAPIClient("http://example.com/api")
        await client.apost("/users", data=schema_data)

    expected_data = {"name": "Test User", "email": "test@example.com", "age": 25}
    assert captured["json"] == expected_data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apost_excludes_none_fields():
    """Ensure None fields in schema data are excluded for async POST."""
    captured = {}
    schema_data = DummySchema(name="Test User", email=None)

    async def fake_apost(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1, "status": "created"})

    with patch.object(httpx.AsyncClient, "post", new=fake_apost):
        client = AutoAPIClient("http://example.com/api")
        await client.apost("/users", data=schema_data)

    assert captured["json"] == {"name": "Test User"}


# Async PUT Tests
@pytest.mark.unit
@pytest.mark.asyncio
async def test_aput_basic():
    """Test basic async PUT request functionality."""
    captured = {}
    data = {"name": "Updated User", "email": "updated@example.com"}

    async def fake_aput(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json)
        request = httpx.Request("PUT", url)
        return httpx.Response(200, request=request, json={"id": 1, **data})

    with patch.object(httpx.AsyncClient, "put", new=fake_aput):
        client = AutoAPIClient("http://example.com/api")
        result = await client.aput("/users/1", data=data)

    assert captured["url"] == "http://example.com/api/users/1"
    assert captured["json"] == data
    assert result == {"id": 1, **data}


# Async PATCH Tests
@pytest.mark.unit
@pytest.mark.asyncio
async def test_apatch_basic():
    """Test basic async PATCH request functionality."""
    captured = {}
    data = {"status": "inactive"}

    async def fake_apatch(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json)
        request = httpx.Request("PATCH", url)
        return httpx.Response(
            200, request=request, json={"id": 1, "status": "inactive", "name": "User"}
        )

    with patch.object(httpx.AsyncClient, "patch", new=fake_apatch):
        client = AutoAPIClient("http://example.com/api")
        await client.apatch("/users/1", data=data)

    assert captured["url"] == "http://example.com/api/users/1"
    assert captured["json"] == data


# Async DELETE Tests
@pytest.mark.unit
@pytest.mark.asyncio
async def test_adelete_basic():
    """Test basic async DELETE request functionality."""
    captured = {}

    async def fake_adelete(self, url, *, headers=None):
        captured.update(url=url, headers=headers)
        request = httpx.Request("DELETE", url)
        return httpx.Response(204, request=request)

    with patch.object(httpx.AsyncClient, "delete", new=fake_adelete):
        client = AutoAPIClient("http://example.com/api")
        result = await client.adelete("/users/1")

    assert captured["url"] == "http://example.com/api/users/1"
    assert result is None  # 204 No Content


@pytest.mark.unit
@pytest.mark.asyncio
async def test_adelete_with_response():
    """Test async DELETE request that returns data."""

    async def fake_adelete(self, url, *, headers=None):
        request = httpx.Request("DELETE", url)
        return httpx.Response(
            200, request=request, json={"message": "User deleted successfully"}
        )

    with patch.object(httpx.AsyncClient, "delete", new=fake_adelete):
        client = AutoAPIClient("http://example.com/api")
        result = await client.adelete("/users/1")

    assert result == {"message": "User deleted successfully"}


# Async Error Handling Tests
@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_rest_http_error():
    """Test async REST request with HTTP error."""

    async def fake_aget(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        response = httpx.Response(404, request=request)
        response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=request, response=response
            )
        )
        return response

    with patch.object(httpx.AsyncClient, "get", new=fake_aget):
        client = AutoAPIClient("http://example.com/api")
        with pytest.raises(httpx.HTTPStatusError):
            await client.aget("/users/999")


# Async Complex Filter Tests
@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_with_complex_filters():
    """Test async GET request with complex nested filter parameters."""
    captured = {}
    complex_filters = {
        "filter": {
            "and": [
                {"field": "status", "operator": "in", "value": ["active", "pending"]},
                {
                    "field": "created_at",
                    "operator": "between",
                    "value": ["2023-01-01", "2023-12-31"],
                },
                {
                    "or": [
                        {"field": "role", "operator": "eq", "value": "admin"},
                        {
                            "field": "permissions",
                            "operator": "contains",
                            "value": "write",
                        },
                    ]
                },
            ]
        },
        "sort": [
            {"field": "name", "direction": "asc"},
            {"field": "created_at", "direction": "desc"},
        ],
        "pagination": {"page": 1, "per_page": 25},
        "include": ["profile", "roles", "permissions"],
    }

    async def fake_aget(self, url, *, params=None, headers=None):
        captured.update(params=params)
        request = httpx.Request("GET", url)
        return httpx.Response(
            200, request=request, json={"items": [], "meta": {"total": 0}}
        )

    with patch.object(httpx.AsyncClient, "get", new=fake_aget):
        client = AutoAPIClient("http://example.com/api")
        await client.aget("/users", params=complex_filters)

    assert captured["params"] == complex_filters


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apost_with_nested_data():
    """Test async POST request with nested data structure."""
    captured = {}
    nested_data = {
        "user": {
            "personal_info": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
            },
            "preferences": {
                "theme": "dark",
                "notifications": {"email": True, "push": False, "sms": True},
            },
            "roles": ["user", "contributor"],
            "metadata": {
                "source": "api",
                "created_by": "admin",
                "tags": ["new_user", "beta_tester"],
            },
        }
    }

    async def fake_apost(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1, "status": "created"})

    with patch.object(httpx.AsyncClient, "post", new=fake_apost):
        client = AutoAPIClient("http://example.com/api")
        await client.apost("/users", data=nested_data)

    assert captured["json"] == nested_data


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,http_method,success_code",
    [
        ("apost", "POST", 201),
        ("aput", "PUT", 202),
        ("apatch", "PATCH", 202),
        ("adelete", "DELETE", 202),
    ],
)
@pytest.mark.parametrize("status_code", [False, True])
@pytest.mark.parametrize("raise_status", [True, False])
@pytest.mark.parametrize("is_error", [False, True])
async def test_async_crud_status_combinations(
    method, http_method, success_code, status_code, raise_status, is_error
):
    """Ensure async CRUD helpers handle status_code and raise_status flags."""

    async def fake(self, url, **kw):
        code = 500 if is_error else success_code
        payload = {"detail": "fail"} if is_error else {"ok": True}
        request = httpx.Request(http_method, url)
        return httpx.Response(code, request=request, json=payload)

    httpx_method = method[1:]
    with patch.object(httpx.AsyncClient, httpx_method, new=fake):
        client = AutoAPIClient("http://example.com/api")
        func = getattr(client, method)

        async def call():
            kwargs = {"status_code": status_code, "raise_status": raise_status}
            if method != "adelete":
                kwargs["data"] = {"foo": "bar"}
            return await func("/ping", **kwargs)

        if is_error and raise_status:
            with pytest.raises(httpx.HTTPStatusError):
                await call()
            return

        result = await call()
        expected_payload = {False: {"ok": True}, True: {"detail": "fail"}}[is_error]
        expected_status = 500 if is_error else success_code
        if status_code:
            payload, code = result
            assert code == expected_status
        else:
            payload = result
        assert payload == expected_payload
