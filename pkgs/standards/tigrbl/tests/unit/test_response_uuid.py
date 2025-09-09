from __future__ import annotations

import json
from uuid import uuid4

from tigrbl.v3.response.shortcuts import as_json


def test_as_json_serializes_uuid() -> None:
    uid = uuid4()
    resp = as_json({"id": uid}, envelope=False)
    assert resp.media_type == "application/json"
    assert json.loads(resp.body) == {"id": str(uid)}
