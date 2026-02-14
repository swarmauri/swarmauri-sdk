"""Lesson 20.1: Mounting favicons from bound ``TigrblApi`` helpers.

This lesson demonstrates direct usage of ``api.mount_favicon(...)`` after
binding the system helper to the API class.
"""

from fastapi.testclient import TestClient

from tigrbl import TigrblApi


def test_api_mount_favicon_default_route() -> None:
    """Mount ``/favicon.ico`` on an API using the bound helper."""
    api = TigrblApi()

    # Pedagogical pattern: use the bound helper directly from the API object.
    api.mount_favicon(name="lesson_api_default_favicon")

    with TestClient(api) as client:
        response = client.get("/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")


def test_api_mount_favicon_custom_route() -> None:
    """Mount a custom favicon path when branding routes are namespaced."""
    api = TigrblApi()
    api.mount_favicon(path="/brand/favicon.ico", name="lesson_api_brand_favicon")

    with TestClient(api) as client:
        response = client.get("/brand/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
