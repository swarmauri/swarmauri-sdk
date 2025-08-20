"""IOSpec integration tests covering schema exposure and defaults."""

from types import SimpleNamespace

from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from autoapi.v3.bindings.model import bind
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.specs import F, IO, S, acol
from autoapi.v3.tables import Base
from autoapi.v3.runtime.atoms.resolve import assemble
from autoapi.v3.runtime.atoms.schema import collect_in, collect_out


class VerbThing(Base, GUIDPk):
    """Model used to verify in/out verb exposure effects."""

    __tablename__ = "verb_things"
    __allow_unmapped__ = True

    code: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(allow_in=False, allow_out=False),
    )


class DefaultThing(Base, GUIDPk):
    """Model used to verify default_factory resolution."""

    __tablename__ = "default_things"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",)),
        default_factory=lambda ctx: "anon",
    )


bind(VerbThing)
bind(DefaultThing)


def test_verb_flags_control_schema_and_storage() -> None:
    """In/Out verbs govern schema exposure while keeping storage intact."""

    specs = VerbThing.__autoapi_cols__
    ctx_in = SimpleNamespace(specs=specs, op="create", temp={})
    collect_in.run(None, ctx_in)
    schema_in = ctx_in.temp["schema_in"]
    assert "code" not in schema_in["by_field"]

    ctx_out = SimpleNamespace(specs=specs, op="read", temp={})
    collect_out.run(None, ctx_out)
    schema_out = ctx_out.temp["schema_out"]
    assert "code" not in schema_out["by_field"]

    assert isinstance(VerbThing.__table__.c.code, Column)
    assert "code" in VerbThing.__autoapi_cols__


def test_default_factory_populates_absent_values() -> None:
    """default_factory supplies a value when the input is absent."""

    specs = DefaultThing.__autoapi_cols__
    ctx = SimpleNamespace(
        specs=specs, temp={"in_values": {}}, persist=True, op="create"
    )
    assemble.run(None, ctx)

    assert ctx.temp["assembled_values"]["name"] == "anon"
    assert ctx.temp["used_default_factory"] == ("name",)
