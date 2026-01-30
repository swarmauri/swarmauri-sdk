import httpx
import pytest
from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String

from examples._support import pick_unused_port, run_uvicorn_app, stop_server


@pytest.mark.asyncio
async def test_diagnostics_hookz_reports_hooks():
    """Teach how hook diagnostics surface registered hooks.

    Purpose:
        Verify that ``/hookz`` is reachable after binding hooks to a model and
        that the endpoint responds successfully.

    What this shows:
        - Hook registrations are collected when the API binds the model.
        - Diagnostics endpoints can surface hook metadata.

    Best practice:
        Use hook diagnostics to validate hook wiring during development before
        relying on them in production flows.
    """

    # Setup: declare a model and a hook to surface in diagnostics.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_hookz_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        def audit(cls, ctx):
            return None

    # Deployment: create the app, include the model, and attach diagnostics.
    app = TigrblApp(engine=mem(async_=False), system_prefix="")
    app.include_model(Widget)
    app.initialize()
    app.attach_diagnostics()

    # Test: bind the model so hooks are registered before we query diagnostics.
    app.bind(Widget)

    # Deployment: run the app under Uvicorn.
    port = pick_unused_port()
    handle = await run_uvicorn_app(app, port=port)
    # Test: request the hook diagnostics endpoint.
    async with httpx.AsyncClient(base_url=handle.base_url, timeout=10.0) as client:
        response = await client.get("/hookz")
        # Assertion: the endpoint responds successfully.
        assert response.status_code == 200
    await stop_server(handle)


def test_hook_registry_tracks_custom_hook():
    """Reinforce that hook registration is reflected in the model registry.

    Purpose:
        Confirm that hook metadata is stored on the model after binding so
        diagnostics endpoints have accurate data to report.

    What this shows:
        - ``hook_ctx`` adds hook definitions to the model.
        - Binding creates per-operation hook buckets.

    Best practice:
        Bind the model before relying on diagnostics to ensure hook metadata is
        collected and consistent.
    """

    # Setup: declare a model with a hook for create operations.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_hook_registry_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="POST_COMMIT")
        def audit(cls, ctx):
            return None

    # Deployment: bind the model through an API to populate hook metadata.
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)
    app.initialize()
    app.bind(Widget)

    # Test: inspect the hook registry on the model.
    hooks = getattr(Widget.hooks, "create")

    # Assertion: the POST_COMMIT hook is tracked after binding.
    assert len(hooks.POST_COMMIT) == 1
