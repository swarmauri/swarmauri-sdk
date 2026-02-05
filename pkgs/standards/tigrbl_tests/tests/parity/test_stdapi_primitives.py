from tigrbl.deps import stdapi


def test_request_parses_json_and_query_params():
    req = stdapi.Request(
        method="POST",
        path="/",
        headers={"content-type": "application/json"},
        query={"a": ["1"], "b": ["2", "3"]},
        path_params={},
        body=b'{"x": 1}',
    )
    assert req.json() == {"x": 1}
    assert req.query_param("a") == "1"
    assert req.query_param("missing", default="fallback") == "fallback"
    assert req.query_params == {"a": "1", "b": "2"}


def test_response_helpers_and_status_line():
    payload = {"ok": True}
    response = stdapi.Response.json(payload, status_code=201, headers={"X-Test": "1"})
    assert response.status_line() == "201 Created"
    assert response.body
    assert ("content-type", "application/json; charset=utf-8") in response.headers
    assert ("x-test", "1") in response.headers

    html_response = stdapi.Response.html("<p>hi</p>")
    assert html_response.status_code == 200
    assert html_response.body == b"<p>hi</p>"

    text_response = stdapi.Response.text("ok")
    assert text_response.body == b"ok"


def test_http_exception_tracks_details():
    exc = stdapi.HTTPException(status_code=403, detail="Forbidden", headers={"x": "y"})
    assert exc.status_code == 403
    assert exc.detail == "Forbidden"
    assert exc.headers == {"x": "y"}
