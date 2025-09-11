from tigrbl.types import (
    App,
    Column,
    InstrumentedAttribute,
    Integer,
    Mapped,
    SimpleNamespace,
    String,
)
from sqlalchemy.orm import DeclarativeBase

from tigrbl.bindings.model import bind
from tigrbl.bindings.rest.router import _build_router
from tigrbl.op import OpSpec
from tigrbl.runtime.atoms.resolve import assemble
from tigrbl.runtime.atoms.schema import collect_in, collect_out
from tigrbl.runtime.kernel import _default_kernel as K
from tigrbl.schema import _build_list_params
from tigrbl.specs import ColumnSpec, F, IO, S, acol, vcol
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk


class _Base(DeclarativeBase):
    """Local base that materializes ColumnSpecs to SQLAlchemy Columns."""

    def __init_subclass__(cls, **kw):
        from tigrbl.orm.tables._base import _materialize_colspecs_to_sqla

        _materialize_colspecs_to_sqla(cls)
        super().__init_subclass__(**kw)


def test_iospec_aliases_affect_schemas() -> None:
    class Thing(Base):
        __tablename__ = "iospec_schema"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(
                in_verbs=("create",),
                out_verbs=("read",),
                alias_in="first_name",
                alias_out="firstName",
            ),
        )

    bind(Thing)
    specs = Thing.__tigrbl_cols__
    ov_in = K._compile_opview_from_specs(specs, SimpleNamespace(alias="create"))
    ctx_in = SimpleNamespace(opview=ov_in, temp={})
    collect_in.run(None, ctx_in)
    schema_in = ctx_in.temp["schema_in"]
    assert "id" not in schema_in["by_field"]
    assert schema_in["by_field"]["name"]["alias_in"] == "first_name"

    ov_out = K._compile_opview_from_specs(specs, SimpleNamespace(alias="read"))
    ctx_out = SimpleNamespace(opview=ov_out, temp={})
    collect_out.run(None, ctx_out)
    schema_out = ctx_out.temp["schema_out"]
    assert "id" in schema_out["by_field"]
    assert schema_out["by_field"]["name"]["alias_out"] == "firstName"


def test_iospec_filter_ops_and_sortable_in_list_params() -> None:
    class Thing(_Base):
        __tablename__ = "iospec_list"

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True),
            io=IO(out_verbs=("read", "list")),
        )
        name: Mapped[str] = acol(
            storage=S(type_=String),
            io=IO(out_verbs=("read", "list"), filter_ops=("eq", "like"), sortable=True),
        )

    params = _build_list_params(Thing)
    fields = set(params.model_fields.keys())
    assert "name__like" in fields
    assert "sort" in fields


def test_iospec_default_factory_resolves_absent_values() -> None:
    class Thing(Base):
        __tablename__ = "iospec_defaults"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read",)),
        )
        created_at: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",)),
            default_factory=lambda ctx: "now",  # simple sentinel
        )

    bind(Thing)
    specs = Thing.__tigrbl_cols__
    ov = K._compile_opview_from_specs(specs, SimpleNamespace(alias="create"))
    ctx = SimpleNamespace(opview=ov, temp={"in_values": {}}, persist=True)
    assemble.run(None, ctx)
    assembled = ctx.temp["assembled_values"]
    assert assembled["created_at"] == "now"
    assert "created_at" in ctx.temp["used_default_factory"]


def test_iospec_bindings_attach_to_model() -> None:
    class Thing(Base):
        __tablename__ = "iospec_bind"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True),
            io=IO(out_verbs=("read",)),
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    bind(Thing)
    assert hasattr(Thing, "schemas")
    assert "name" in Thing.__tigrbl_cols__


def test_iospec_in_verbs_reflected_in_openapi() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_openapi"
        __allow_unmapped__ = True

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    sp_create = OpSpec(alias="create", target="create")
    sp_read = OpSpec(alias="read", target="read")
    router = _build_router(Widget, [sp_create, sp_read])
    app = App()
    app.include_router(router)
    spec = app.openapi()

    create_props = spec["components"]["schemas"]["WidgetCreateRequest"]["properties"]
    assert "name" in create_props
    assert "id" not in create_props


def test_iospec_virtual_columns_materialized_and_tracked() -> None:
    class Thing(Base):
        __tablename__ = "iospec_storage"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True),
            io=IO(out_verbs=("read",)),
        )
        nickname: str = vcol(
            field=F(py_type=str),
            io=IO(out_verbs=("read",)),
        )

    bind(Thing)
    assert isinstance(Thing.__table__.c.id, Column)
    assert "nickname" in Thing.__table__.c
    assert isinstance(Thing.__dict__["nickname"], InstrumentedAttribute)
    assert isinstance(Thing.__tigrbl_cols__["nickname"], ColumnSpec)
