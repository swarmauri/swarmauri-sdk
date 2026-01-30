from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from typing import Any, Callable, Iterable

import httpx
import uvicorn

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.system import stop_uvicorn_server
from tigrbl.types import (
    App,
    ARRAY,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    JSON,
    JSONB,
    LargeBinary,
    Numeric,
    PgEnum,
    PgUUID,
    SAEnum,
    String,
    TSVECTOR,
    TZDateTime,
    Text,
    UniqueConstraint,
)


@dataclass
class UvicornHandle:
    base_url: str
    server: uvicorn.Server
    task: asyncio.Task


def pick_unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def build_widget_model(
    name: str = "Widget",
    *,
    use_specs: bool = False,
    with_table_args: Iterable[Any] | None = None,
    extra_attrs: dict[str, Any] | None = None,
) -> type:
    attrs: dict[str, Any] = {
        "__tablename__": f"{name.lower()}s",
        "__allow_unmapped__": True,
    }
    if use_specs:
        attrs["name"] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str, description="Display name"),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )
    else:
        attrs["name"] = Column(String, nullable=False)

    if with_table_args:
        attrs["__table_args__"] = tuple(with_table_args)

    if extra_attrs:
        attrs.update(extra_attrs)

    return type(name, (Base, GUIDPk), attrs)


def build_type_gallery_model() -> type:
    class TypeGallery(Base, GUIDPk):
        __tablename__ = "type_gallery"
        __allow_unmapped__ = True

        text = Column(Text)
        boolean = Column(Boolean)
        integer = Column(Integer)
        numeric = Column(Numeric(10, 2))
        json = Column(JSON)
        datetime = Column(DateTime)
        tzdatetime = Column(TZDateTime)
        binary = Column(LargeBinary)
        enum = Column(SAEnum("alpha", "beta", name="enum_kind"))
        array = Column(ARRAY(Integer))
        jsonb = Column(JSONB)
        pgenum = Column(PgEnum("red", "blue", name="pg_enum_kind"))
        pguuid = Column(PgUUID(as_uuid=True))
        tsvector = Column(TSVECTOR)

    return TypeGallery


def build_simple_api(model: type) -> TigrblApp:
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(model)
    api.initialize()
    return api


def collect_aliases(api: TigrblApp, model: type) -> set[str]:
    return {spec.alias for spec in api.bind(model)}


def get_op_spec(api: TigrblApp, model: type, alias: str):
    for spec in api.bind(model):
        if spec.alias == alias:
            return spec
    raise KeyError(f"Missing op alias: {alias}")


def build_fastapi_app(api: TigrblApp) -> App:
    app = App()
    app.include_router(api.router)
    return app


def build_app_with_jsonrpc_and_diagnostics(
    model: type,
    *,
    system_prefix: str = "",
    jsonrpc_prefix: str = "/rpc",
) -> tuple[App, TigrblApp]:
    api = TigrblApp(engine=mem(async_=False), system_prefix=system_prefix)
    api.include_model(model)
    api.initialize()
    api.mount_jsonrpc(prefix=jsonrpc_prefix)
    app = build_fastapi_app(api)
    api.attach_diagnostics(prefix=system_prefix, app=app)
    return app, api


async def run_uvicorn_app(app: App, *, port: int) -> UvicornHandle:
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    base_url = f"http://127.0.0.1:{port}"
    await wait_for_http(base_url + "/healthz")
    return UvicornHandle(base_url=base_url, server=server, task=task)


async def wait_for_http(url: str, *, timeout: float = 5.0) -> None:
    async with httpx.AsyncClient(timeout=timeout) as client:
        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            try:
                response = await client.get(url)
                if response.status_code < 500:
                    return
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.1)
            if asyncio.get_event_loop().time() > deadline:
                raise RuntimeError(f"Timed out waiting for {url}")


async def stop_server(handle: UvicornHandle) -> None:
    await stop_uvicorn_server(handle.server, handle.task)


def build_constraints() -> list[Any]:
    return [
        UniqueConstraint("name", name="uq_widget_name"),
        CheckConstraint("length(name) > 0", name="ck_widget_name"),
    ]


def build_rest_payload(name: str) -> dict[str, Any]:
    return {"name": name}


def model_route(model: type) -> str:
    return f"/{model.__name__.lower()}"


def build_api_client(endpoint: str) -> httpx.Client:
    return httpx.Client(base_url=endpoint, timeout=10.0)


def build_async_client(endpoint: str) -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=endpoint, timeout=10.0)


def build_rpc_payload(method: str, params: dict[str, Any]) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }


def app_spec_config_mro(*bases: type) -> Callable[[], type]:
    def _builder() -> type:
        return type("LessonApp", bases, {})

    return _builder
