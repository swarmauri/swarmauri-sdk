from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from tigrbl.requests import Request
from tigrbl.responses import Response

ADMIN_KEY = "admin-secret"


def _json_mapping(response: Response) -> Mapping[str, Any]:
    payload = response.json()
    if not isinstance(payload, Mapping):
        raise TypeError("Expected a mapping JSON payload")
    if isinstance(payload.get("result"), Mapping):
        return payload["result"]
    if isinstance(payload.get("data"), Mapping):
        return payload["data"]
    return payload


def _rest_request(
    method: str,
    path: str,
    payload: dict[str, Any],
    response_payload: Mapping[str, Any],
) -> tuple[Request, Response, Mapping[str, Any]]:
    request = Request(
        method=method,
        path=path,
        headers={"x-admin-key": ADMIN_KEY, "content-type": "application/json"},
        query={},
        path_params={},
        body=json.dumps(payload).encode("utf-8"),
    )
    response = Response.json(response_payload)
    return request, response, _json_mapping(response)


def test_rest_request_supports_mapping_access_on_result_payload() -> None:
    request, response, result = _rest_request(
        "POST",
        "/users",
        {"email": "a@b.com"},
        {"ok": True, "result": {"id": "u-1", "email": "a@b.com"}},
    )

    assert request.headers.get("x-admin-key") == ADMIN_KEY
    assert request.json()["email"] == "a@b.com"
    assert response.status_code == 200
    assert isinstance(result, Mapping)
    assert result["id"] == "u-1"
    assert result.get("email") == "a@b.com"


def test_rest_request_supports_mapping_access_on_data_payload() -> None:
    request, _, data = _rest_request(
        "POST",
        "/users",
        {"email": "e@f.com"},
        {"ok": True, "data": {"id": "u-3", "email": "e@f.com"}},
    )

    assert request.headers.get("x-admin-key") == ADMIN_KEY
    assert request.json().get("email") == "e@f.com"
    assert isinstance(data, Mapping)
    assert data["id"] == "u-3"
    assert data.get("email") == "e@f.com"


def test_rest_request_supports_mapping_access_without_result_envelope() -> None:
    request, _, data = _rest_request(
        "GET",
        "/users/u-2",
        {},
        {"id": "u-2", "email": "c@d.com"},
    )

    assert request.headers.get("x-admin-key") == ADMIN_KEY
    assert isinstance(data, Mapping)
    assert data["id"] == "u-2"
    assert data.get("email") == "c@d.com"


def test_response_json_is_mapping_and_supports_data_and_result_access() -> None:
    response = Response.json(
        {
            "ok": True,
            "data": {"id": "d-1", "name": "data-object"},
            "result": {"id": "r-1", "name": "result-object"},
        }
    )

    payload = response.json()
    assert isinstance(payload, Mapping)
    assert payload["data"]["id"] == "d-1"
    assert payload["result"]["id"] == "r-1"
