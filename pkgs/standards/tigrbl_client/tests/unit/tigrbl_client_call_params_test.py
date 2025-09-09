import json
from unittest.mock import patch

import httpx
import pytest

from tigrbl_client import TigrblClient


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
def test_call_serializes_schema_params():
    schema = DummySchema(foo="bar", num=1)
    captured = {}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": None}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = TigrblClient("http://example.com")
        client.call("dummy", params=schema)

    assert captured["json"]["params"] == {"foo": "bar", "num": 1}


@pytest.mark.unit
def test_call_excludes_none_fields():
    schema = DummySchema(foo="bar", num=None)
    captured = {}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": None}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = TigrblClient("http://example.com")
        client.call("dummy", params=schema)

    assert captured["json"]["params"] == {"foo": "bar"}


@pytest.mark.unit
def test_call_uses_dict_params():
    params = {"a": 1, "b": 2}
    captured = {}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": None}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = TigrblClient("http://example.com")
        client.call("dummy", params=params)

    assert captured["json"]["params"] == params


@pytest.mark.unit
def test_call_defaults_to_empty_params():
    captured = {}

    def fake_post(self, url, *, json=None, headers=None):
        captured.update(json=json)
        request = httpx.Request("POST", url)
        return httpx.Response(
            200, request=request, json={"jsonrpc": "2.0", "result": None}
        )

    with patch.object(httpx.Client, "post", new=fake_post):
        client = TigrblClient("http://example.com")
        client.call("dummy")

    assert captured["json"]["params"] == {}
