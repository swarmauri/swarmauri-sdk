import inspect

import pytest
from tigrbl.orm.tables import Base
from tigrbl.types import (
    InstrumentedAttribute,
    Integer,
    SimpleNamespace,
    String,
)

from tigrbl.bindings import (
    api as api_binding,
    columns as columns_binding,
    handlers as handlers_binding,
    hooks as hooks_binding,
    model as model_binding,
    rest as rest_binding,
    rpc as rpc_binding,
)
from tigrbl.bindings.schemas import build_and_attach as schemas_build_and_attach
from tigrbl.specs import ColumnSpec, F, IO, S
from tigrbl.op import resolve
from tigrbl.runtime import executor as _executor
from tigrbl.column import shortcuts as sc


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
async def test_api_include_and_rpc_call(monkeypatch, model_cls):
    model_binding.bind(model_cls)
    api = SimpleNamespace()
    api_binding.include_model(api, model_cls, mount_router=False)
    assert model_cls.__name__ in api.models
    routers = api_binding.include_models(
        SimpleNamespace(), [model_cls], mount_router=False
    )
    assert model_cls.__name__ in routers

    async def fake_invoke(*, request, db, phases, ctx):  # noqa: D401
        return ctx["payload"]

    monkeypatch.setattr(_executor, "_invoke", fake_invoke)
    payload = {"name": "x"}
    result = await api_binding.rpc_call(
        api, model_cls, "create", payload=payload, db=object()
    )
    assert result == payload


@pytest.mark.i9n
def test_column_spec_io_flags():
    spec = ColumnSpec(
        storage=S(type_=String),
        field=F(py_type=str),
        io=IO(in_verbs=(), out_verbs=("read",)),
    )
    assert "create" not in spec.io.in_verbs
    assert "read" in spec.io.out_verbs
