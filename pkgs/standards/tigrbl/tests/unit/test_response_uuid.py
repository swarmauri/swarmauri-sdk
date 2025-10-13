from __future__ import annotations

import base64
import json
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
