from types import SimpleNamespace


from tigrbl.bindings.model import bind
from tigrbl.runtime.atoms.schema import collect_in, collect_out
from tigrbl.specs import F, IO, S, acol, vcol
from tigrbl.orm.tables import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped


def test_field_spec_py_type_overrides_annotation():
    class Thing(Base):
        __tablename__ = "things_py_type"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
            io=IO(),
        )
        nickname: int = vcol(
            field=F(py_type=str),
            io=IO(out_verbs=("read",)),
        )

    bind(Thing)
    specs = Thing.__tigrbl_cols__
    ctx = SimpleNamespace(specs=specs, op="read", temp={})
    collect_out.run(None, ctx)
    schema_out = ctx.temp["schema_out"]
    assert schema_out["by_field"]["nickname"]["py_type"] == "str"


def test_field_spec_constraints_affect_sqla_column():
    class Item(Base):
        __tablename__ = "items_constraints"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(constraints={"max_length": 10}),
        )

    bind(Item)
    assert Item.__table__.c.name.type.length == 10


def test_field_spec_required_in_marks_field_required():
    class Product(Base):
        __tablename__ = "products_required_in"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(required_in=("create",)),
            io=IO(in_verbs=("create",)),
        )

    bind(Product)
    specs = Product.__tigrbl_cols__
    ctx = SimpleNamespace(specs=specs, op="create", temp={})
    collect_in.run(None, ctx)
    schema_in = ctx.temp["schema_in"]
    assert schema_in["by_field"]["name"]["required"] is True


def test_field_spec_allow_null_in_overrides_nullable():
    class Profile(Base):
        __tablename__ = "profiles_allow_null"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True),
        )
        bio: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(allow_null_in=("update",)),
            io=IO(in_verbs=("create", "update")),
        )

    bind(Profile)
    specs = Profile.__tigrbl_cols__
    ctx = SimpleNamespace(specs=specs, op="update", temp={})
    collect_in.run(None, ctx)
    schema_in = ctx.temp["schema_in"]
    # The storage layer marks ``bio`` as non-nullable; ``allow_null_in`` only
    # relaxes nullability when the storage layer permits it. Expect the field to
    # remain non-nullable in the inbound schema.
    assert schema_in["by_field"]["bio"]["nullable"] is False
