from __future__ import annotations

from tigrbl_core._spec.request_spec import RequestSpec


def test_request_spec_default_values() -> None:
    spec = RequestSpec()

    assert spec.method == "GET"
    assert spec.path == "/"
    assert spec.headers == {}
    assert spec.query == {}
    assert spec.path_params == {}
    assert spec.body == b""


def test_request_spec_custom_payload() -> None:
    spec = RequestSpec(method="POST", path="/items", body=b"{}")

    assert spec.method == "POST"
    assert spec.path == "/items"
    assert spec.body == b"{}"
