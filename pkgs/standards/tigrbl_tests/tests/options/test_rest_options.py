from httpx import ASGITransport, Client
import pytest

import pytest

from tigrbl import TigrblApp
from tigrbl.responses import Response


<<<<<<< HEAD
@pytest.mark.xfail(
    raises=AttributeError,
    reason="TigrblApp no longer exposes REST verb decorator helpers such as .get/.post.",
)
=======
@pytest.mark.xfail(reason="TigrblApp no longer exposes HTTP verb decorator methods")
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
def test_rest_options_automatic_allow_header() -> None:
    app = TigrblApp()

    @app.get("/health")
    async def health() -> Response:
        return Response.json({"ok": True})

    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        response = client.options("/health")

    assert response.status_code == 204
    assert response.text == ""
    allow = {item.strip() for item in response.headers["allow"].split(",")}
    assert allow == {"GET", "OPTIONS"}
    assert response.headers["access-control-allow-methods"] == "GET,OPTIONS"


<<<<<<< HEAD
@pytest.mark.xfail(
    raises=AttributeError,
    reason="TigrblApp no longer exposes REST verb decorator helpers such as .get/.post.",
)
=======
@pytest.mark.xfail(reason="TigrblApp no longer exposes HTTP verb decorator methods")
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
def test_rest_options_handles_cors_preflight_headers() -> None:
    app = TigrblApp()

    @app.post("/submit")
    async def submit() -> Response:
        return Response.json({"saved": True})

    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        response = client.options(
            "/submit",
            headers={
                "Origin": "https://frontend.example",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )

    assert response.status_code == 204
    assert response.headers["access-control-allow-origin"] == "https://frontend.example"
    assert (
        response.headers["access-control-allow-headers"] == "authorization,content-type"
    )
    assert response.headers["vary"] == "origin,access-control-request-headers"
