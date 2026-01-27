import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from tigrbl.op.mro_collect import mro_collect_decorated_ops
from tigrbl.op import op_ctx
from tigrbl.response.shortcuts import as_file
from tigrbl.bindings import (
    build_hooks,
    build_handlers,
    build_rest,
    build_schemas,
    register_rpc,
    include_model,
)
from tigrbl.types import App as FastApp
from tigrbl.types import Integer, Mapped, mapped_column
from tigrbl.table import Table
from tigrbl.api._api import Api
from tigrbl.app._app import App as BaseApp


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
        specs = list(mro_collect_decorated_ops(Widget))
        build_schemas(Widget, specs)
        build_hooks(Widget, specs)
        build_handlers(Widget, specs)
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

    api.get_db = fake_db  # type: ignore[assignment]
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

    api.get_db = fake_db  # type: ignore[assignment]
    include_model(api, Widget)

    class FilesApp(BaseApp):
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
