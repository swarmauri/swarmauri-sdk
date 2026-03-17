import asyncio
from pathlib import Path

from httpx import ASGITransport, Client

from tests.conftest import mro_collect_decorated_ops
from tigrbl_concrete._mapping.router.include import include_table
from tigrbl.decorators.op import op_ctx
from tigrbl.shortcuts.responses import as_file
from tigrbl import (
    build_hooks,
    build_handlers,
    build_rest,
    build_schemas,
    register_rpc,
)
from tigrbl import TigrblApp
from tigrbl.types import Integer, Mapped, mapped_column
from tigrbl import Table
from tigrbl import TigrblRouter


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
    app = TigrblApp()
    app.include_router(router_provider)
    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        response = client.post("/widget/download", json={})
        return response


def test_file_response_ops(tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_text("content")
    Widget = _build_model(object, file_path)

    resp = asyncio.run(Widget.ops.by_alias["download"][0].core_raw({}))
    assert resp.path == str(file_path)

    response = _server_client_roundtrip(Widget.rest.router)
    assert response.status_code == 200
    assert response.content == file_path.read_bytes()


def test_file_response_table(tmp_path):
    file_path = tmp_path / "table.txt"
    file_path.write_text("table")
    Widget = _build_model(Table, file_path, bind=True)

    resp = asyncio.run(Widget.ops.by_alias["download"][0].core_raw({}))
    assert resp.path == str(file_path)

    response = _server_client_roundtrip(Widget.rest.router)
    assert response.status_code == 200
    assert response.content == file_path.read_bytes()


def test_file_response_api(tmp_path):
    file_path = tmp_path / "router.txt"
    file_path.write_text("api")
    Widget = _build_model(Table, file_path, bind=False)
    Widget.columns = ()

    router = TigrblRouter(prefix="")

    async def fake_db():
        yield None

    router.get_db = fake_db  # type: ignore[assignment]
    include_table(router, Widget)

    resp = asyncio.run(Widget.ops.by_alias["download"][0].core_raw({}))
    assert resp.path == str(file_path)

    app = TigrblApp()
    app.include_router(router)
    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        response = client.post("/widget/download", json={})
        assert response.status_code == 200
        assert response.content == file_path.read_bytes()
