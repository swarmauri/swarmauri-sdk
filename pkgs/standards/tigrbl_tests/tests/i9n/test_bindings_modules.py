import inspect

import pytest
from tigrbl_base._base._rpc_map import register_and_attach, rpc_call
from tigrbl_concrete._mapping.model import (
    _bind_model_hooks,
    _materialize_handlers,
    _materialize_rest_router,
    _materialize_schemas,
    bind,
    rebind,
)
from tigrbl_concrete._mapping.op_resolver import resolve
from tigrbl_concrete._mapping.router.include import include_table, include_tables
from tigrbl_core._spec.column_spec import mro_collect_columns
from tigrbl.shortcuts import column as sc
from tigrbl.orm.tables import TableBase
from tigrbl._spec import IO, ColumnSpec, F, S
from tigrbl.types import (
    InstrumentedAttribute,
    Integer,
    SimpleNamespace,
    String,
)


def _make_model():
    TableBase.metadata.clear()

    class Item(TableBase):  # type: ignore[misc]
        __tablename__ = "items"

        id = sc.acol(
            storage=sc.S(type_=Integer, primary_key=True),
            field=sc.F(py_type=int),
            io=sc.IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
        name = sc.acol(
            storage=sc.S(type_=String, nullable=False),
            field=sc.F(py_type=str),
            io=sc.IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
            ),
        )

    return Item


@pytest.fixture
def model_cls():
    return _make_model()


@pytest.fixture
def specs(model_cls):
    return resolve(model_cls)


@pytest.mark.i9n
def test_columns_build_and_attach(model_cls):
    cols = mro_collect_columns(model_cls)
    assert "name" in cols
    assert isinstance(model_cls.__dict__["name"], InstrumentedAttribute)


@pytest.mark.i9n
def test_schemas_build_and_attach(model_cls, specs):
    _materialize_schemas(model_cls, tuple(specs))
    assert hasattr(model_cls.schemas.create, "in_")
    assert hasattr(model_cls.schemas.read, "out")


@pytest.mark.i9n
def test_hooks_normalize_and_attach(model_cls, specs):
    _bind_model_hooks(model_cls, tuple(specs))
    # default transactional steps are no longer injected
    assert not model_cls.hooks.create.START_TX
    assert not model_cls.hooks.create.END_TX


@pytest.mark.i9n
def test_handlers_build_and_attach(model_cls, specs):
    _materialize_handlers(model_cls, tuple(specs))
    _bind_model_hooks(model_cls, tuple(specs))
    assert model_cls.ops.by_alias["create"].target == "create"
    assert model_cls.hooks.create.HANDLER


@pytest.mark.i9n
def test_rpc_register_and_attach(model_cls, specs):
    _materialize_schemas(model_cls, tuple(specs))
    register_and_attach(model_cls, specs)
    assert inspect.iscoroutinefunction(model_cls.rpc.create)


@pytest.mark.i9n
def test_rest_build_router_and_attach(model_cls, specs):
    _materialize_handlers(model_cls, tuple(specs))
    _bind_model_hooks(model_cls, tuple(specs))
    _materialize_schemas(model_cls, tuple(specs))
    _materialize_rest_router(model_cls, tuple(specs), router=None)
    router = model_cls.rest.router
    assert router is not None
    assert getattr(router, "routes", [])


@pytest.mark.i9n
def test_model_bind_and_rebind(model_cls):
    bound = bind(model_cls)
    assert model_cls.ops.by_alias["create"]
    again = rebind(model_cls)
    assert len(again) == len(bound)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_router_include_and_rpc_call_returns_operation_envelope(model_cls):
    bind(model_cls)
    router = SimpleNamespace()
    include_table(router, model_cls, mount_router=False)
    assert model_cls.__name__ in router.tables
    routers = include_tables(SimpleNamespace(), [model_cls], mount_router=False)
    assert model_cls.__name__ in routers

    payload = {"id": 1, "name": "x"}
    result = await rpc_call(router, model_cls, "create", payload=payload, db=object())
    assert result["model"] is model_cls
    assert result["alias"] == "create"
    assert result["target"] == "create"
    assert result["payload"] == payload
    assert result["ctx"]["payload"] == payload
    assert "phases" not in result
    assert callable(result["serialize"])


@pytest.mark.i9n
def test_column_spec_io_flags():
    spec = ColumnSpec(
        storage=S(type_=String),
        field=F(py_type=str),
        io=IO(in_verbs=(), out_verbs=("read",)),
    )
    assert "create" not in spec.io.in_verbs
    assert "read" in spec.io.out_verbs
