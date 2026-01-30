from __future__ import annotations

from typing import Iterable, Sequence

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.specs import F, IO, S, acol, vcol
from tigrbl.types import App, Integer, String


def make_widget_model(
    *,
    model_name: str = "Widget",
    table_name: str = "widgets",
    resource: str = "widget",
    mixins: Sequence[type] = (),
    include_virtual: bool = False,
) -> type:
    id_col = acol(
        storage=S(type_=Integer, primary_key=True, autoincrement=True),
        io=IO(out_verbs=("read", "list")),
    )
    name_col = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "update", "replace"),
            out_verbs=("read", "list"),
        ),
    )
    attrs: dict[str, object] = {
        "__tablename__": table_name,
        "__resource__": resource,
        "__allow_unmapped__": True,
        "id": id_col,
        "name": name_col,
        "__tigrbl_cols__": {"id": id_col, "name": name_col},
    }
    if include_virtual:
        label_col = vcol(
            field=F(py_type=str),
            io=IO(out_verbs=("read", "list")),
        )
        attrs["label"] = label_col
        attrs["__tigrbl_cols__"]["label"] = label_col
    return type(model_name, (Base, *mixins), attrs)


async def build_widget_app(
    model: type,
    *,
    jsonrpc: bool = True,
    diagnostics_prefixes: Iterable[str] = ("", "/systemz"),
) -> tuple[App, TigrblApp]:
    app = App()
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(model, prefix="")
    await api.initialize()
    if jsonrpc:
        api.mount_jsonrpc()
    for prefix in diagnostics_prefixes:
        api.attach_diagnostics(prefix=prefix, app=app)
    app.include_router(api.router)
    return app, api
