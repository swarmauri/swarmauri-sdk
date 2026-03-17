import pytest
from httpx import ASGITransport, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import Mapped, sessionmaker
from sqlalchemy.pool import StaticPool
from tigrbl import TigrblApp
from tigrbl.shortcuts.engine import engine as engine_factory
from tigrbl.shortcuts.engine import mem
from tigrbl_concrete._mapping.model import bind
from tests.conftest import _build_router
from tigrbl_base._base._rpc_map import register_and_attach
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl_atoms.atoms.resolve import assemble
from tigrbl_atoms.atoms.schema.collect_in import _run as collect_in_run
from tigrbl_atoms.atoms.schema.collect_out import _run as collect_out_run
from tigrbl_kernel import _default_kernel as K
from tigrbl_kernel import build_phase_chains
from tigrbl._spec import IO, F, S
from tigrbl.shortcuts.column import acol, vcol
from tigrbl.types import Integer as IntType
from tigrbl.types import SimpleNamespace
from tigrbl.types import String as StrType


@pytest.mark.i9n
def test_request_and_response_schemas_respect_iospec_aliases():
    class Thing(TableBase):
        __tablename__ = "iospec_schema_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(
                in_verbs=("create",),
                out_verbs=("read",),
                alias_in="first_name",
                alias_out="firstName",
            ),
        )

    bind(Thing)
    specs = Thing.__tigrbl_cols__
    ctx_in = SimpleNamespace(
        opview=K._compile_opview_from_specs(specs, SimpleNamespace(alias="create")),
        op="create",
        temp={},
    )
    collect_in_run(None, ctx_in)
    schema_in = ctx_in.temp["schema_in"]
    assert "id" not in schema_in["by_field"]
    assert schema_in["by_field"]["name"]["alias_in"] == "first_name"

    ctx_out = SimpleNamespace(
        opview=K._compile_opview_from_specs(specs, SimpleNamespace(alias="read")),
        op="read",
        temp={},
    )
    collect_out_run(None, ctx_out)
    schema_out = ctx_out.temp["schema_out"]
    assert "id" in schema_out["by_field"]
    assert schema_out["by_field"]["name"]["alias_out"] == "firstName"


@pytest.mark.i9n
def test_columns_materialized_for_acol():
    class Thing(TableBase):
        __tablename__ = "iospec_columns_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True), io=IO(out_verbs=("read",))
        )
        nick: Mapped[str] = vcol(field=F(py_type=str), io=IO(out_verbs=("read",)))

    bind(Thing)
    assert "id" in Thing.__table__.c
    assert "nick" in Thing.__table__.c


@pytest.mark.i9n
def test_default_factory_resolves_missing_value():
    class Thing(TableBase):
        __tablename__ = "iospec_defaults_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        created = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",)),
            default_factory=lambda ctx: "now",
        )

    bind(Thing)
    specs = Thing.__tigrbl_cols__
    ctx = SimpleNamespace(
        opview=K._compile_opview_from_specs(specs, SimpleNamespace(alias="create")),
        op="create",
        temp={"in_values": {}},
        persist=True,
    )
    assemble._run(None, ctx)
    assembled = ctx.temp["assembled_values"]
    assert assembled["created"] == "now"
    assert "created" in ctx.temp["used_default_factory"]


@pytest.mark.i9n
def test_binding_attaches_internal_model_namespaces():
    class Thing(TableBase):
        __tablename__ = "iospec_internal_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True), io=IO(out_verbs=("read",))
        )
        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    app = TigrblApp()
    app.include_table(Thing, mount_router=False)
    assert "Thing" in app.tables
    assert hasattr(app.schemas, "Thing")
    assert "name" in Thing.__tigrbl_cols__


@pytest.mark.i9n
def test_openapi_reflects_io_verbs():
    class Widget(TableBase, GUIDPk):
        __tablename__ = "iospec_openapi_i9n"
        __allow_unmapped__ = True

        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    sp_create = OpSpec(alias="create", target="create")
    sp_read = OpSpec(alias="read", target="read")
    router = _build_router(Widget, [sp_create, sp_read])
    app = TigrblApp()
    app.include_router(router)
    spec = app.openapi()

    props_create = spec["components"]["schemas"]["WidgetCreateRequest"]["properties"]
    assert "name" in props_create
    assert "id" not in props_create

    props_read = spec["components"]["schemas"]["WidgetReadResponse"]["properties"]
    assert "name" in props_read
    assert "id" in props_read


@pytest.mark.i9n
def test_storage_and_sqlalchemy_integration():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    TableBase.metadata.clear()

    class Thing(TableBase):
        __tablename__ = "iospec_storage_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Thing)
    TableBase.metadata.create_all(engine)

    with SessionLocal() as session:
        obj = Thing(name="foo")
        session.add(obj)
        session.commit()
        session.refresh(obj)
        assert obj.id is not None
        stored = session.get(Thing, obj.id)
        assert stored.name == "foo"


@pytest.mark.i9n
def test_rest_call_respects_aliases():
    eng = engine_factory(mem(async_=False))

    class Thing(TableBase):
        __tablename__ = "iospec_rest_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    app = TigrblApp(engine=eng)
    app.include_table(Thing)
    TableBase.metadata.create_all(eng.raw()[0])
    transport = ASGITransport(app=app)
    with Client(transport=transport, base_url="http://test") as client:
        resp = client.post("/thing", json={"name": "Ada"})
        data = resp.json()
        assert data["name"] == "Ada"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rpc_call_uses_schemas():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    TableBase.metadata.clear()

    class Thing(TableBase):
        __tablename__ = "iospec_rpc_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Thing)
    register_and_attach(Thing, [OpSpec(alias="create", target="create")])
    TableBase.metadata.create_all(engine)

    with SessionLocal() as session:
        result = await Thing.rpc.create({"name": "Bob"}, db=session)
    assert result["model"] is Thing
    assert result["alias"] == "create"
    assert result["payload"]["name"] == "Bob"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_core_crud_helpers_operate():
    eng = engine_factory(mem(async_=False))

    class Thing(TableBase):
        __tablename__ = "iospec_core_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    app = TigrblApp(engine=eng)
    app.include_table(Thing)
    TableBase.metadata.create_all(eng.raw()[0])

    with eng.session() as session:
        created = await app.core.Thing.create({"name": "Zed"}, db=session)
        obj = await app.core.Thing.read({"id": created["id"]}, db=session)
    assert obj["name"] == "Zed"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_hooks_trigger_with_iospec():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    called = {}

    async def before(ctx):
        called["hit"] = True

    class Thing(TableBase):
        __tablename__ = "iospec_hooks_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )
        __tigrbl_hooks__ = {"create": {"PRE_HANDLER": [before]}}

    bind(Thing)
    register_and_attach(Thing, [OpSpec(alias="create", target="create")])
    TableBase.metadata.create_all(engine)

    with SessionLocal() as session:
        result = await Thing.rpc.create({"name": "hi"}, db=session)
    assert result["model"] is Thing
    assert called.get("hit") is None


@pytest.mark.i9n
def test_atoms_execute_with_iospec():
    class Thing(TableBase):
        __tablename__ = "iospec_atoms_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Thing)
    specs = Thing.__tigrbl_cols__
    ctx = SimpleNamespace(
        opview=K._compile_opview_from_specs(specs, SimpleNamespace(alias="create")),
        op="create",
        temp={"in_values": {"name": "x"}},
        persist=True,
    )
    collect_in_run(None, ctx)
    assemble._run(None, ctx)
    collect_out_run(None, ctx)
    assert ctx.temp["assembled_values"]["name"] == "x"


@pytest.mark.i9n
def test_system_phase_chain_includes_system_steps():
    class Thing(TableBase):
        __tablename__ = "iospec_system_i9n"
        __allow_unmapped__ = True

        id = acol(
            storage=S(type_=IntType, primary_key=True), io=IO(out_verbs=("read",))
        )
        name = acol(
            storage=S(type_=StrType, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Thing)
    chains = build_phase_chains(Thing, "create")
    assert "HANDLER" in chains
    assert any(chains[ph] for ph in chains)
