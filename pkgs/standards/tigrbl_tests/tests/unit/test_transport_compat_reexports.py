from __future__ import annotations

from tigrbl.headers import Headers
from tigrbl.requests import Request
from tigrbl.responses import Response
from tigrbl.transport import finalize_transport_response


def test_transport_primitives_reexport_from_legacy_modules() -> None:
    req = Request(method="GET", path="/", headers={"x-a": "1"})
    assert isinstance(req.headers, Headers)

    resp = Response.json({"ok": True})
    headers, body = finalize_transport_response(
        {"method": "GET"},
        resp.status_code,
        [(k.encode("latin-1"), v.encode("latin-1")) for k, v in resp.headers.items()],
        resp.body,
    )
    assert body
    assert any(k == b"content-length" for k, _ in headers)
