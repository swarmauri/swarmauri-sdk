import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from autoapi.v3.decorators import collect_decorated_ops, op_ctx
from autoapi.v3.response.shortcuts import as_file
from autoapi.v3.bindings import (
    build_hooks,
    build_handlers,
    build_rest,
    build_schemas,
    register_rpc,
    include_model,
)
from autoapi.v3.runtime import plan as runtime_plan
from autoapi.v3.types import App as FastApp
from autoapi.v3.types import Integer, Mapped, mapped_column
from autoapi.v3.table import Table
from autoapi.v3.api._api import Api
from autoapi.v3.app._app import App as AutoApp


def _build_model(base: type, file_path: Path, *, bind: bool = True) -> type:
    if issubclass(base, Table):

        class Widget(base):
            __tablename__ = "widget"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)

            @op_ctx(
                alias="download", target="custom", arity="collection", persist="none"
            )
            def download(cls, ctx):
                return as_file(file_path)
    else:

        class Widget(base):
            @op_ctx(
                alias="download", target="custom", arity="collection", persist="none"
            )
            def download(cls, ctx):
                return as_file(file_path)

    if bind:
        specs = list(collect_decorated_ops(Widget))
        build_schemas(Widget, specs)
        build_hooks(Widget, specs)
        build_handlers(Widget, specs)
        runtime_plan.attach_atoms_for_model(Widget, {})
        build_rest(Widget, specs)
        register_rpc(Widget, specs)
    return Widget


def _server_client_roundtrip(router_provider):
    app = FastApp()
    app.include_router(router_provider)
    client = TestClient(app)
    response = client.post("/widget/download", json={})
    return response


def test_file_response_ops(tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_text("content")
    Widget = _build_model(object, file_path)

    resp = asyncio.run(Widget.handlers.download.handler({}))
    assert resp.path == str(file_path)

    response = _server_client_roundtrip(Widget.rest.router)
    assert response.status_code == 200
    assert response.content == file_path.read_bytes()


def test_file_response_table(tmp_path):
    file_path = tmp_path / "table.txt"
    file_path.write_text("table")
    Widget = _build_model(Table, file_path, bind=False)

    resp = asyncio.run(Widget.handlers.download.handler({}))
    assert resp.path == str(file_path)

    response = _server_client_roundtrip(Widget.rest.router)
    assert response.status_code == 200
    assert response.content == file_path.read_bytes()


def test_file_response_api(tmp_path):
    file_path = tmp_path / "api.txt"
    file_path.write_text("api")
    Widget = _build_model(Table, file_path, bind=False)
    Widget.columns = ()

    class FilesApi(Api):
        PREFIX = ""

    api = FilesApi()

    async def fake_db():
        yield None

    def fake_sync_db():
        yield None

    api.get_async_db = fake_db  # type: ignore[assignment]
    api.get_db = fake_sync_db  # type: ignore[assignment]
    include_model(api, Widget)

    resp = asyncio.run(Widget.handlers.download.handler({}))
    assert resp.path == str(file_path)

    app = FastApp()
    app.include_router(api)
    client = TestClient(app)
    response = client.post("/widget/download", json={})
    assert response.status_code == 200
    assert response.content == file_path.read_bytes()


def test_file_response_app(tmp_path):
    file_path = tmp_path / "app.txt"
    file_path.write_text("app")
    Widget = _build_model(Table, file_path, bind=False)
    Widget.columns = ()

    class FilesApi(Api):
        PREFIX = ""

    api = FilesApi()

    async def fake_db():
        yield None

    def fake_sync_db():
        yield None

    api.get_async_db = fake_db  # type: ignore[assignment]
    api.get_db = fake_sync_db  # type: ignore[assignment]
    include_model(api, Widget)

    class FilesApp(AutoApp):
        TITLE = "FilesApp"
        VERSION = "0.1.0"
        LIFESPAN = None

    app = FilesApp()
    app.include_router(api)

    resp = asyncio.run(Widget.handlers.download.handler({}))
    assert resp.path == str(file_path)

    client = TestClient(app)
    response = client.post("/widget/download", json={})
    assert response.status_code == 200
    assert response.content == file_path.read_bytes()
