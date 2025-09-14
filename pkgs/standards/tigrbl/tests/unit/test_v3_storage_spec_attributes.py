from types import SimpleNamespace

from tigrbl.runtime.atoms.storage import to_stored
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)
from tigrbl.specs import S, acol
from tigrbl.column.storage_spec import ForeignKeySpec, StorageTransform
from tigrbl.orm.tables import Base
from sqlalchemy import Integer, String, text
from sqlalchemy.orm import Mapped


# type_


def test_type_spec_sets_column_type():
    class Thing(Base):
        __tablename__ = "type_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        name: Mapped[str] = acol(storage=S(type_=String))

    assert isinstance(Thing.__table__.c.name.type, String)


# nullable


def test_nullable_false_sets_column_non_nullable():
    class Thing(Base):
        __tablename__ = "nullable_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        name: Mapped[str] = acol(storage=S(type_=String, nullable=False))

    assert Thing.__table__.c.name.nullable is False


# unique


def test_unique_sets_column_unique():
    class Thing(Base):
        __tablename__ = "unique_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        email: Mapped[str] = acol(storage=S(type_=String, unique=True))

    assert Thing.__table__.c.email.unique is True


# index


def test_index_creates_index_on_column():
    class Thing(Base):
        __tablename__ = "index_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        value: Mapped[int] = acol(storage=S(type_=Integer, index=True))

    col = Thing.__table__.c.value
    assert col.index is True
    assert any(col.name in idx.columns for idx in Thing.__table__.indexes)


# primary_key


def test_primary_key_flag_sets_pk():
    class Thing(Base):
        __tablename__ = "pk_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))

    assert Thing.__table__.c.id.primary_key is True


# autoincrement


def test_autoincrement_flag_propagates():
    class Thing(Base):
        __tablename__ = "ai_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )

    assert Thing.__table__.c.id.autoincrement is True


# default


def test_default_value_is_assigned():
    class Thing(Base):
        __tablename__ = "default_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        count: Mapped[int] = acol(storage=S(type_=Integer, default=5))

    assert Thing.__table__.c.count.default.arg == 5


# onupdate


def test_onupdate_callable_is_set():
    def bump():
        return 1

    class Thing(Base):
        __tablename__ = "onupdate_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        updated: Mapped[int] = acol(storage=S(type_=Integer, onupdate=bump))

    assert callable(Thing.__table__.c.updated.onupdate.arg)


# server_default


def test_server_default_clause_attached():
    class Thing(Base):
        __tablename__ = "server_default_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        flag: Mapped[int] = acol(storage=S(type_=Integer, server_default=text("1")))

    sd = Thing.__table__.c.flag.server_default
    assert sd is not None and sd.arg.text == "1"


# refresh_on_return


def test_refresh_on_return_preserved_in_spec():
    class Thing(Base):
        __tablename__ = "refresh_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        code: Mapped[str] = acol(storage=S(type_=String, refresh_on_return=True))

    spec = Thing.__tigrbl_cols__["code"].storage
    assert getattr(spec, "refresh_on_return") is True


# transform


def test_transform_applied_during_persist():
    transform = StorageTransform(to_stored=lambda v, ctx: v.upper())

    class Thing(Base):
        __tablename__ = "transform_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        name: Mapped[str] = acol(storage=S(type_=String, transform=transform))

    app = SimpleNamespace()
    alias = "create"
    ov = OpView(
        schema_in=SchemaIn(fields=("name",), by_field={"name": {}}),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={},
        virtual_producers={},
        to_stored_transforms={"name": transform.to_stored},
        refresh_hints=(),
    )
    K._opviews[app] = {(Thing, alias): ov}
    K._primed[app] = True
    ctx = SimpleNamespace(
        app=app,
        model=Thing,
        op=alias,
        persist=True,
        temp={"assembled_values": {"name": "abc"}},
    )
    to_stored.run(None, ctx)
    assert ctx.temp["assembled_values"]["name"] == "ABC"


# foreign key


def test_foreign_key_spec_creates_fk():
    class Parent(Base):
        __tablename__ = "parent_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))

    class Child(Base):
        __tablename__ = "child_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        parent_id: Mapped[int] = acol(
            storage=S(type_=Integer, fk=ForeignKeySpec(target="parent_spec.id"))
        )

    fk = next(iter(Child.__table__.c.parent_id.foreign_keys))
    assert str(fk.column) == "parent_spec.id"


# check constraint


def test_check_constraint_attached():
    class Thing(Base):
        __tablename__ = "check_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        value: Mapped[int] = acol(storage=S(type_=Integer, check="value > 0"))

    spec = Thing.__tigrbl_cols__["value"].storage
    assert spec.check == "value > 0"


# comment


def test_comment_is_set_on_column():
    class Thing(Base):
        __tablename__ = "comment_spec"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(storage=S(type_=Integer, primary_key=True))
        notes: Mapped[str] = acol(storage=S(type_=String, comment="sample"))

    assert Thing.__table__.c.notes.comment == "sample"
