import inspect

import pytest
import tigrbl.mapping.columns as columns_binding
import tigrbl.mapping.handlers as handlers_binding
import tigrbl.mapping.hooks as hooks_binding
import tigrbl.mapping.model as model_binding
import tigrbl.mapping.rest as rest_binding
import tigrbl.mapping.router as router_binding
import tigrbl.mapping.rpc as rpc_binding
from tigrbl import column as sc
from tigrbl.mapping.schemas import build_and_attach as schemas_build_and_attach
from tigrbl.mapping.op_resolver import resolve
from tigrbl.orm.tables import Base
from tigrbl._spec import IO, ColumnSpec, F, S
from tigrbl.types import (
    InstrumentedAttribute,
    Integer,
    SimpleNamespace,
    String,
)


def _make_model():
    Base.metadata.clear()

    class Item(Base):  # type: ignore[misc]
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
    columns_binding.build_and_attach(model_cls)
    assert hasattr(model_cls, "__tigrbl_cols__")
    assert "name" in model_cls.__tigrbl_cols__
    assert isinstance(model_cls.__dict__["name"], InstrumentedAttribute)


@pytest.mark.i9n
def test_schemas_build_and_attach(model_cls, specs):
    columns_binding.build_and_attach(model_cls)
    schemas_build_and_attach(model_cls, specs)
    assert hasattr(model_cls.schemas.create, "in_")
    assert hasattr(model_cls.schemas.read, "out")


@pytest.mark.i9n
def test_hooks_normalize_and_attach(model_cls, specs):
    columns_binding.build_and_attach(model_cls)
    hooks_binding.normalize_and_attach(model_cls, specs)
    # default transactional steps are no longer injected
    assert not model_cls.hooks.create.START_TX
    assert not model_cls.hooks.create.END_TX


@pytest.mark.i9n
def test_handlers_build_and_attach(model_cls, specs):
    columns_binding.build_and_attach(model_cls)
    handlers_binding.build_and_attach(model_cls, specs)
    assert callable(model_cls.handlers.create.raw)
    assert model_cls.hooks.create.HANDLER


@pytest.mark.i9n
def test_rpc_register_and_attach(model_cls, specs):
    columns_binding.build_and_attach(model_cls)
    rpc_binding.register_and_attach(model_cls, specs)
    assert inspect.iscoroutinefunction(model_cls.rpc.create)


@pytest.mark.i9n
def test_rest_build_router_and_attach(model_cls, specs):
    columns_binding.build_and_attach(model_cls)
    rest_binding.build_router_and_attach(model_cls, specs)
    router = model_cls.rest.router
    assert router is not None
    assert getattr(router, "routes", [])


@pytest.mark.i9n
def test_model_bind_and_rebind(model_cls):
    specs = model_binding.bind(model_cls)
    assert model_cls.handlers.create
    again = model_binding.rebind(model_cls)
    assert len(again) == len(specs)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_router_include_and_rpc_call_returns_operation_envelope(model_cls):
    model_binding.bind(model_cls)
    router = SimpleNamespace()
    router_binding.include_table(router, model_cls, mount_router=False)
    assert model_cls.__name__ in router.tables
    routers = router_binding.include_tables(
        SimpleNamespace(), [model_cls], mount_router=False
    )
    assert model_cls.__name__ in routers

    payload = {"name": "x"}
    result = await router_binding.rpc_call(
        router, model_cls, "create", payload=payload, db=object()
    )
    assert result["model"] is model_cls
    assert result["alias"] == "create"
    assert result["target"] == "create"
    assert result["payload"] == payload
    assert isinstance(result["phases"], dict)
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
