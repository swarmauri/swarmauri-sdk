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


# GET Tests
@pytest.mark.unit
def test_get_basic():
    """Test basic GET request functionality."""
    captured = {}

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url, params=params, headers=headers)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"id": 1, "name": "test"})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com/api")
        result = client.get("/users/1")

    assert captured["url"] == "http://example.com/api/users/1"
    assert result == {"id": 1, "name": "test"}


@pytest.mark.unit
def test_get_with_params():
    """Test GET request with query parameters."""
    captured = {}

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(url=url, params=params)
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"items": [], "total": 0})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com/api")
        client.get("/users", params={"page": 1, "limit": 10, "status": "active"})

    assert captured["params"] == {"page": 1, "limit": 10, "status": "active"}


@pytest.mark.unit
def test_get_with_filter_params():
    """Test GET request with complex filter parameters."""
    captured = {}
    filter_params = {
        "filter[name][like]": "john%",
        "filter[age][gte]": 18,
        "filter[status][in]": "active,pending",
        "sort": "-created_at,name",
        "include": "profile,posts",
    }

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(params=params)
        request = httpx.Request("GET", url)
        return httpx.Response(
            200, request=request, json={"items": [], "meta": {"total": 0}}
        )

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com/api")
        client.get("/users", params=filter_params)

    assert captured["params"] == filter_params


@pytest.mark.unit
def test_get_with_schema():
    """Test GET request with output schema validation."""

    def fake_get(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        return httpx.Response(200, request=request, json={"name": "test", "value": 42})

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com/api")
        result = client.get("/items/1", out_schema=DummySchema)

    assert isinstance(result, DummySchema)
    assert result._data == {"name": "test", "value": 42}


# POST Tests
@pytest.mark.unit
def test_post_basic():
    """Test basic POST request functionality."""
    captured = {}
    data = {"name": "New User", "email": "user@example.com"}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json, headers=headers)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1, **data})

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        result = client.post("/users", data=data)

    assert captured["url"] == "http://example.com/api/users"
    assert captured["json"] == data
    assert captured["headers"]["Content-Type"] == "application/json"
    assert result == {"id": 1, **data}


@pytest.mark.unit
def test_post_with_schema_data():
    """Test POST request with Pydantic schema data."""
    captured = {}
    schema_data = DummySchema(name="Test User", email="test@example.com", age=25)

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1, "status": "created"})

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        client.post("/users", data=schema_data)

    expected_data = {"name": "Test User", "email": "test@example.com", "age": 25}
    assert captured["json"] == expected_data


@pytest.mark.unit
def test_post_excludes_none_fields():
    """Ensure None fields in schema data are excluded."""
    captured = {}
    schema_data = DummySchema(name="Test User", email=None)

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1, "status": "created"})

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        client.post("/users", data=schema_data)

    assert captured["json"] == {"name": "Test User"}


# PUT Tests
@pytest.mark.unit
def test_put_basic():
    """Test basic PUT request functionality."""
    captured = {}
    data = {"name": "Updated User", "email": "updated@example.com"}

    def fake_put(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json)
        request = httpx.Request("PUT", url)
        return httpx.Response(200, request=request, json={"id": 1, **data})

    with patch.object(httpx.Client, "put", new=fake_put):
        client = AutoAPIClient("http://example.com/api")
        result = client.put("/users/1", data=data)

    assert captured["url"] == "http://example.com/api/users/1"
    assert captured["json"] == data
    assert result == {"id": 1, **data}


# PATCH Tests
@pytest.mark.unit
def test_patch_basic():
    """Test basic PATCH request functionality."""
    captured = {}
    data = {"status": "inactive"}

    def fake_patch(self, url, *, json=None, headers=None):
        captured.update(url=url, json=json)
        request = httpx.Request("PATCH", url)
        return httpx.Response(
            200, request=request, json={"id": 1, "status": "inactive", "name": "User"}
        )

    with patch.object(httpx.Client, "patch", new=fake_patch):
        client = AutoAPIClient("http://example.com/api")
        client.patch("/users/1", data=data)

    assert captured["url"] == "http://example.com/api/users/1"
    assert captured["json"] == data


# DELETE Tests
@pytest.mark.unit
def test_delete_basic():
    """Test basic DELETE request functionality."""
    captured = {}

    def fake_delete(self, url, *, headers=None):
        captured.update(url=url, headers=headers)
        request = httpx.Request("DELETE", url)
        return httpx.Response(204, request=request)

    with patch.object(httpx.Client, "delete", new=fake_delete):
        client = AutoAPIClient("http://example.com/api")
        result = client.delete("/users/1")

    assert captured["url"] == "http://example.com/api/users/1"
    assert result is None  # 204 No Content


@pytest.mark.unit
def test_delete_with_response():
    """Test DELETE request that returns data."""

    def fake_delete(self, url, *, headers=None):
        request = httpx.Request("DELETE", url)
        return httpx.Response(
            200, request=request, json={"message": "User deleted successfully"}
        )

    with patch.object(httpx.Client, "delete", new=fake_delete):
        client = AutoAPIClient("http://example.com/api")
        result = client.delete("/users/1")

    assert result == {"message": "User deleted successfully"}


# Error Handling Tests
@pytest.mark.unit
def test_rest_http_error():
    """Test REST request with HTTP error."""

    def fake_get(self, url, *, params=None, headers=None):
        request = httpx.Request("GET", url)
        response = httpx.Response(404, request=request)
        response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=request, response=response
            )
        )
        return response

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com/api")
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/users/999")


# Complex Filter Tests
@pytest.mark.unit
def test_get_with_complex_filters():
    """Test GET request with complex nested filter parameters."""
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

    def fake_get(self, url, *, params=None, headers=None):
        captured.update(params=params)
        request = httpx.Request("GET", url)
        return httpx.Response(
            200, request=request, json={"items": [], "meta": {"total": 0}}
        )

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com/api")
        client.get("/users", params=complex_filters)

    assert captured["params"] == complex_filters


@pytest.mark.unit
def test_post_with_nested_data():
    """Test POST request with nested data structure."""
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

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(201, request=request, json={"id": 1, "status": "created"})

    with patch.object(httpx.Client, "post", new=fake_post):
        client = AutoAPIClient("http://example.com/api")
        client.post("/users", data=nested_data)

    assert captured["json"] == nested_data


@pytest.mark.unit
@pytest.mark.parametrize("status_code", [False, True])
@pytest.mark.parametrize("raise_status", [True, False])
@pytest.mark.parametrize("is_error", [False, True])
def test_get_status_combinations(status_code, raise_status, is_error):
    """Cover all flag combinations for GET status handling."""

    def fake_get(self, url, *, params=None, headers=None):
        code = 404 if is_error else 200
        payload = {"detail": "Not found"} if is_error else {"ok": True}
        request = httpx.Request("GET", url)
        return httpx.Response(code, request=request, json=payload)

    with patch.object(httpx.Client, "get", new=fake_get):
        client = AutoAPIClient("http://example.com/api")

        def call():
            return client.get(
                "/ping", status_code=status_code, raise_status=raise_status
            )

        if is_error and raise_status:
            with pytest.raises(httpx.HTTPStatusError):
                call()
            return

        result = call()
        expected_payload = {
            False: {"ok": True},
            True: {"detail": "Not found"},
        }[is_error]
        expected_status = 404 if is_error else 200
        if status_code:
            payload, status = result
            assert status == expected_status
        else:
            payload = result
        assert payload == expected_payload


@pytest.mark.unit
@pytest.mark.parametrize(
    "method,http_method,success_code",
    [
        ("post", "POST", 201),
        ("put", "PUT", 202),
        ("patch", "PATCH", 202),
        ("delete", "DELETE", 202),
    ],
)
@pytest.mark.parametrize("status_code", [False, True])
@pytest.mark.parametrize("raise_status", [True, False])
@pytest.mark.parametrize("is_error", [False, True])
def test_crud_status_combinations(
    method, http_method, success_code, status_code, raise_status, is_error
):
    """Ensure CRUD helpers handle status_code and raise_status flags."""

    def fake(self, url, **kw):
        code = 500 if is_error else success_code
        payload = {"detail": "fail"} if is_error else {"ok": True}
        request = httpx.Request(http_method, url)
        return httpx.Response(code, request=request, json=payload)

    with patch.object(httpx.Client, method, new=fake):
        client = AutoAPIClient("http://example.com/api")
        func = getattr(client, method)

        def call():
            kwargs = {"status_code": status_code, "raise_status": raise_status}
            if method != "delete":
                kwargs["data"] = {"foo": "bar"}
            return func("/ping", **kwargs)

        if is_error and raise_status:
            with pytest.raises(httpx.HTTPStatusError):
                call()
            return

        result = call()
        expected_payload = {False: {"ok": True}, True: {"detail": "fail"}}[is_error]
        expected_status = 500 if is_error else success_code
        if status_code:
            payload, code = result
            assert code == expected_status
        else:
            payload = result
        assert payload == expected_payload
