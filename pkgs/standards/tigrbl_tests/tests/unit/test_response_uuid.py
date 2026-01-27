from __future__ import annotations

import base64
import importlib
import json
import sys
import types
from uuid import uuid4


from tigrbl.response.shortcuts import as_json


def test_as_json_serializes_uuid() -> None:
    uid = uuid4()
    resp = as_json({"id": uid}, envelope=False)
    assert resp.media_type == "application/json"
    assert json.loads(resp.body) == {"id": str(uid)}


def test_as_json_serializes_bytes() -> None:
    payload = b"\x00\x01bytes"
    resp = as_json({"blob": payload}, envelope=False)
    assert resp.media_type == "application/json"
    body = json.loads(resp.body)
    assert body == {"blob": base64.b64encode(payload).decode("ascii")}


def test_as_json_fallbacks_when_orjson_unsupported(monkeypatch) -> None:
    import tigrbl.response.shortcuts as shortcuts

    original_orjson = sys.modules.get("orjson")
    fake_orjson = types.SimpleNamespace(
        OPT_NON_STR_KEYS=0,
        OPT_SERIALIZE_NUMPY=0,
        OPT_SERIALIZE_BYTES=0,
        dumps=lambda *args, **kwargs: (_ for _ in ()).throw(
            TypeError("unsupported option")
        ),
    )

    monkeypatch.setitem(sys.modules, "orjson", fake_orjson)
    reloaded = importlib.reload(shortcuts)

    try:
        payload = {"blob": b"\x00\x98bytes"}
        resp = reloaded.as_json(payload, envelope=False)

        assert resp.media_type == "application/json"
        assert json.loads(resp.body) == {
            "blob": base64.b64encode(payload["blob"]).decode("ascii")
        }
    finally:
        if original_orjson is not None:
            monkeypatch.setitem(sys.modules, "orjson", original_orjson)
        else:
            monkeypatch.delitem(sys.modules, "orjson", raising=False)
        importlib.reload(shortcuts)
