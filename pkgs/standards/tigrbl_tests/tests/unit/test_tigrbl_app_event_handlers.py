import pytest

from tigrbl import TigrblApp


@pytest.mark.unit
def test_add_event_handler_registers_startup_handler() -> None:
    app = TigrblApp()

    def handler() -> None:
        return None

    app.add_event_handler("startup", handler)

    assert app.event_handlers["startup"] == [handler]


@pytest.mark.unit
def test_on_event_decorator_registers_shutdown_handler() -> None:
    app = TigrblApp()

    @app.on_event("shutdown")
    def handler() -> None:
        return None

    assert app.event_handlers["shutdown"] == [handler]


@pytest.mark.asyncio
async def test_run_event_handlers_executes_sync_and_async_handlers() -> None:
    app = TigrblApp()
    calls: list[str] = []

    def sync_handler() -> None:
        calls.append("sync")

    async def async_handler() -> None:
        calls.append("async")

    app.add_event_handler("startup", sync_handler)
    app.add_event_handler("startup", async_handler)

    await app.run_event_handlers("startup")

    assert calls == ["sync", "async"]


@pytest.mark.unit
def test_add_event_handler_rejects_unsupported_event_type() -> None:
    app = TigrblApp()

    with pytest.raises(ValueError, match="Unsupported event type"):
        app.add_event_handler("deploy", lambda: None)
