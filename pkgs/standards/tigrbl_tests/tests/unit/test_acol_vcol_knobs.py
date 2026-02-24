from datetime import datetime


from tigrbl.bindings.model import bind
from tigrbl.runtime.atoms.schema import collect_in, collect_out
from tigrbl.runtime.kernel import _default_kernel as K
from tigrbl.specs import ColumnSpec, F, IO, S, acol, vcol
from tigrbl.orm.tables import Base
from tigrbl.types import (
    Column,
    DateTime,
    InstrumentedAttribute,
    Integer,
    Mapped,
    SimpleNamespace,
    String,
)


def test_acol_vcol_knobs_affect_bindings_and_schemas():
    """Ensure acol/vcol knobs influence bindings and schemas."""

    Base.metadata.clear()

    class Thing(Base):
        __tablename__ = "things"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(out_verbs=("read", "list")),
        )

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(constraints={"max_length": 50}, required_in=("create",)),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )

        created_at: Mapped[datetime] = acol(
            storage=S(type_=DateTime, nullable=False),
            io=IO(out_verbs=("read",)),
            default_factory=lambda ctx: datetime(2020, 1, 1),
        )

        nickname: str = vcol(
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
            default_factory=lambda ctx: "anon",
        )

        slug: str = vcol(
            field=F(py_type=str),
            io=IO(out_verbs=("read",)),
            read_producer=lambda obj, ctx: obj.name.lower(),
        )

    bind(Thing)

    specs = Thing.__tigrbl_cols__

    # openapi request schema via collect_in
    ov_in = K._compile_opview_from_specs(specs, Thing.ops.by_alias["create"][0])
    ctx_in = SimpleNamespace(opview=ov_in, op="create", temp={})
    collect_in.run(None, ctx_in)
    schema_in = ctx_in.temp["schema_in"]
    assert schema_in["by_field"]["name"]["required"] is True
    assert schema_in["by_field"]["nickname"]["required"] is False
    assert schema_in["by_field"]["nickname"]["virtual"] is True

    # openapi response schema via collect_out
    ov_out = K._compile_opview_from_specs(specs, Thing.ops.by_alias["read"][0])
    ctx_out = SimpleNamespace(opview=ov_out, op="read", temp={})
    collect_out.run(None, ctx_out)
    schema_out = ctx_out.temp["schema_out"]
    for field in ("name", "created_at", "nickname", "slug"):
        assert field in schema_out["by_field"]
    assert schema_out["by_field"]["slug"]["virtual"] is True

    # binding of schemas on model
    assert hasattr(Thing.schemas, "create") and hasattr(Thing.schemas, "read")

    # binding of columns on model: persisted becomes SQLAlchemy Column, virtual column
    # attribute is instrumented while its ColumnSpec remains recorded
    assert isinstance(Thing.__table__.c.name, Column)
    assert isinstance(Thing.__dict__["slug"], InstrumentedAttribute)
    assert isinstance(Thing.__tigrbl_cols__["slug"], ColumnSpec)
    assert "name" in Thing.__tigrbl_cols__ and "slug" in Thing.__tigrbl_cols__

    # read_producer works on virtual column
    obj = SimpleNamespace(name="TeSt")
    assert Thing.__tigrbl_cols__["slug"].read_producer(obj, {}) == "test"

    # binding of ops on model
    assert "create" in Thing.opspecs.by_alias
    assert "read" in Thing.opspecs.by_alias
