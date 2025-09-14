from __future__ import annotations
from types import SimpleNamespace

from tigrbl.response import (
    ResponseSpec,
    get_attached_response_spec,
    infer_hints,
    response_ctx,
    resolve_response_spec,
)
from tigrbl.api.api_spec import APISpec
from tigrbl.app.app_spec import AppSpec
from tigrbl.op.types import OpSpec
from tigrbl.table.table_spec import TableSpec


def test_response_ctx_precedence():
    @response_ctx(headers={"A": "app"})
    class App:  # pragma: no cover - simple container
        pass

    @response_ctx(headers={"A": "api", "B": "api"})
    class API:  # pragma: no cover - simple container
        pass

    @response_ctx(headers={"A": "table", "C": "table"})
    class Table:  # pragma: no cover - simple container
        pass

    @response_ctx(headers={"A": "op", "D": "op"})
    def op():  # pragma: no cover - simple function
        pass

    app_spec = AppSpec(response=ResponseSpec(status_code=200))
    api_spec = APISpec(response=ResponseSpec(status_code=201))
    table_spec = TableSpec(
        model=SimpleNamespace(), response=ResponseSpec(status_code=202)
    )
    op_spec = OpSpec(alias="x", target="custom", response=ResponseSpec(status_code=203))

    merged = resolve_response_spec(
        app_spec.response,
        api_spec.response,
        table_spec.response,
        op_spec.response,
    )
    merged = resolve_response_spec(
        merged,
        get_attached_response_spec(App),
        get_attached_response_spec(API),
        get_attached_response_spec(Table),
        get_attached_response_spec(op),
    )

    hints, envelope, default_media = infer_hints(merged)
    assert hints.status_code == 203
    assert hints.headers["A"] == "op"
    assert hints.headers["B"] == "api"
    assert hints.headers["C"] == "table"
    assert hints.headers["D"] == "op"
    assert envelope is None
    assert default_media is None
