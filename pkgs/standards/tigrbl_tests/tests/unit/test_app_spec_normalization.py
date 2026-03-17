from __future__ import annotations

import pytest
from sqlalchemy import Integer, String

from tigrbl_core._spec.app_spec import normalize_app_spec
from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec
from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_core._spec.io_spec import IOSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.response_spec import ResponseSpec
from tigrbl_core._spec.router_spec import RouterSpec
from tigrbl_core._spec.schema_spec import SchemaSpec
from tigrbl_core._spec.storage_spec import ForeignKeySpec, StorageSpec
from tigrbl_core._spec.table_spec import TableSpec
from tigrbl_core._spec.response_resolver import resolve_response_spec


def _noop(*_args: object, **_kwargs: object) -> object:
    return None


def test_normalize_app_spec_preserves_max_depth_nested_spec_graph() -> None:
    op_hook = HookSpec(phase="after", fn=_noop, order=10)
    table_schema = SchemaSpec(alias="widget.out", kind="out", schema={"type": "object"})

    widget_table = TableSpec(
        model_ref="pkg.models:Widget",
        response=ResponseSpec(status_code=202),
        ops=(
            OpSpec(
                alias="create_widget",
                target="create",
                response=ResponseSpec(status_code=203),
                hooks=(op_hook,),
                deps=("op-dep",),
                secdeps=("op-secdep",),
            ),
        ),
        columns={
            "id": ColumnSpec(
                storage=StorageSpec(type_=Integer, primary_key=True, nullable=False),
                field=FieldSpec(py_type=int, description="Widget id"),
                io=IOSpec(out_verbs=("read",), sortable=True),
            ),
            "owner_id": ColumnSpec(
                storage=StorageSpec(
                    type_=Integer,
                    nullable=False,
                    fk=ForeignKeySpec(target="owners.id"),
                ),
                field=FieldSpec(py_type=int, required_in=("create",)),
                io=IOSpec(in_verbs=("create",), out_verbs=("read",)),
            ),
            "name": ColumnSpec(
                storage=StorageSpec(type_=String(64), nullable=False),
                field=FieldSpec(py_type=str, constraints={"min_length": 1}),
                io=IOSpec(in_verbs=("create", "update"), out_verbs=("read", "list")),
            ),
        },
        schemas=(table_schema,),
        hooks=(_noop,),
        security_deps=("table-secdep",),
        deps=("table-dep",),
    )

    router = RouterSpec(
        name="widgets",
        prefix="/widgets",
        response=ResponseSpec(status_code=201),
        tags=("Widgets",),
        ops=(),
        schemas=(
            SchemaSpec(alias="router.out", kind="out", schema={"type": "object"}),
        ),
        hooks=(_noop,),
        security_deps=("router-secdep",),
        deps=("router-dep",),
        tables=(widget_table,),
    )

    app_spec = AppSpec(
        title="Widgets",
        version="1.0.0",
        response=ResponseSpec(status_code=200),
        routers=router,
        tables=(),
        ops=(),
        schemas=(SchemaSpec(alias="app.out", kind="out", schema={"type": "object"}),),
        hooks=(_noop,),
        security_deps=("app-secdep",),
        deps=("app-dep",),
        middlewares=("mw",),
    )

    normalized = normalize_app_spec(app_spec)

    assert isinstance(normalized.routers[0], RouterSpec)
    assert isinstance(normalized.routers[0].tables[0], TableSpec)
    assert isinstance(normalized.routers[0].tables[0].ops[0], OpSpec)
    assert isinstance(normalized.routers[0].tables[0].ops[0].hooks[0], HookSpec)
    assert isinstance(normalized.routers[0].tables[0].columns["id"], ColumnSpec)
    assert isinstance(normalized.routers[0].tables[0].columns["id"].io, IOSpec)
    assert isinstance(normalized.routers[0].tables[0].columns["id"].field, FieldSpec)
    assert isinstance(
        normalized.routers[0].tables[0].columns["id"].storage, StorageSpec
    )
    assert isinstance(
        normalized.routers[0].tables[0].columns["owner_id"].storage.fk,
        ForeignKeySpec,
    )
    assert isinstance(normalized.schemas[0], SchemaSpec)
    assert isinstance(normalized.routers[0].schemas[0], SchemaSpec)
    assert isinstance(normalized.routers[0].tables[0].schemas[0], SchemaSpec)


def test_max_depth_response_spec_precedence_prefers_lower_scopes() -> None:
    op_spec = OpSpec(
        alias="read_widget",
        target="read",
        response=ResponseSpec(status_code=204, headers={"x-level": "op"}),
    )
    table_spec = TableSpec(
        model_ref="pkg.models:Widget",
        response=ResponseSpec(status_code=203, headers={"x-level": "table"}),
        ops=(op_spec,),
    )
    router_spec = RouterSpec(
        name="widgets",
        response=ResponseSpec(status_code=202, headers={"x-level": "router"}),
        tables=(table_spec,),
    )
    app_spec = normalize_app_spec(
        AppSpec(
            response=ResponseSpec(status_code=201, headers={"x-level": "app"}),
            routers=(router_spec,),
        )
    )

    merged = resolve_response_spec(
        app_spec.response,
        app_spec.routers[0].response,
        app_spec.routers[0].tables[0].response,
        app_spec.routers[0].tables[0].ops[0].response,
    )

    assert merged is not None
    assert merged.status_code == 204
    assert merged.headers["x-level"] == "op"


@pytest.mark.xfail(strict=True, reason="Spec graph input validation not yet enforced")
def test_normalize_app_spec_rejects_non_spec_router_entries() -> None:
    normalize_app_spec(AppSpec(routers=("not-a-router-spec",)))


@pytest.mark.xfail(strict=True, reason="Spec graph input validation not yet enforced")
def test_normalize_app_spec_rejects_non_spec_table_and_op_entries() -> None:
    router_spec = RouterSpec(
        name="widgets", tables=("not-a-table-spec",), ops=("bad-op",)
    )
    normalize_app_spec(AppSpec(routers=(router_spec,)))


def test_normalize_app_spec_applies_fallback_defaults_for_required_strings() -> None:
    normalized = normalize_app_spec(
        AppSpec(
            title="",
            version="",
            jsonrpc_prefix="",
            system_prefix="",
        )
    )

    assert normalized.title == "Tigrbl"
    assert normalized.version == "0.1.0"
    assert normalized.jsonrpc_prefix == "/rpc"
    assert normalized.system_prefix == "/system"


def test_normalize_app_spec_materializes_router_spec_iterables() -> None:
    routers = (RouterSpec(name="r1"), RouterSpec(name="r2"))
    router_gen = (router for router in routers)

    normalized = normalize_app_spec(AppSpec(routers=router_gen))

    assert normalized.routers == routers
