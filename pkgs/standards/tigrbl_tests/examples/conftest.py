from __future__ import annotations

import pytest
import pytest_asyncio

from tigrbl import Base
from tigrbl.schema import builder as v3_builder
from tigrbl.runtime import kernel as runtime_kernel

from .lesson_support import build_widget_app, make_widget_model
from .uvicorn_support import run_uvicorn_in_task, stop_uvicorn_server


def _reset_tigrbl_state() -> None:
    Base.metadata.clear()
    v3_builder._SchemaCache.clear()
    runtime_kernel._default_kernel = runtime_kernel.Kernel()


@pytest.fixture(autouse=True)
def _reset_state() -> None:
    _reset_tigrbl_state()
    yield
    _reset_tigrbl_state()


@pytest_asyncio.fixture()
async def running_widget_app() -> str:
    widget = make_widget_model()
    app, _ = await build_widget_app(widget)
    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        yield base_url
    finally:
        await stop_uvicorn_server(server, task)
