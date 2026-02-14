"""Lesson 20.2: Mounting favicons on ``TigrblApp``.

This lesson demonstrates app-first mounting with the instance-bound
``mount_favicon`` helper for discoverable bootstrap configuration.
"""

from fastapi.testclient import TestClient

from tigrbl import TigrblApp


def test_app_mount_favicon_default_route() -> None:
    """Mount ``/favicon.ico`` on an app using the convenience helper."""
    app = TigrblApp()

    # A clear, explicit call keeps mount behavior easy to discover.
    app.mount_favicon(name="lesson_app_default_favicon")

    with TestClient(app) as client:
        response = client.get("/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")


def test_app_mount_favicon_custom_route() -> None:
    """Mount a namespaced favicon route for advanced app layouts."""
    app = TigrblApp()

    app.mount_favicon(path="/assets/favicon.ico", name="lesson_app_assets_favicon")

    with TestClient(app) as client:
        response = client.get("/assets/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
