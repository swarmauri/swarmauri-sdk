from autoapi.v3.tables import Base
from autoapi.v3.specs.shortcuts import acol, S
from autoapi.v3.specs.storage_spec import StorageTransform, ForeignKeySpec
from autoapi.v3.types import Integer, String
from sqlalchemy import text


def test_storage_spec_type_instantiated():
    class TypeModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))

    assert isinstance(TypeModel.__table__.c.id.type, Integer)


def test_storage_spec_nullable():
    class NullableModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))
        name = acol(storage=S(type_=String, nullable=False))

    assert NullableModel.__table__.c.name.nullable is False


def test_storage_spec_unique():
    class UniqueModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))
        email = acol(storage=S(type_=String, unique=True))

    assert UniqueModel.__table__.c.email.unique is True


def test_storage_spec_index():
    class IndexModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))
        name = acol(storage=S(type_=String, index=True))

    idx_cols = {tuple(i.columns)[0].name for i in IndexModel.__table__.indexes}
    assert "name" in idx_cols


def test_storage_spec_primary_key():
    class PKModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))

    assert PKModel.__table__.c.id.primary_key is True


def test_storage_spec_autoincrement_flag_preserved():
    spec = S(type_=Integer, primary_key=True, autoincrement=False)

    class AIMModel(Base):
        id = acol(storage=spec)

    assert AIMModel.__autoapi_cols__["id"].storage.autoincrement is False


def test_storage_spec_default_value():
    class DefaultModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))
        score = acol(storage=S(type_=Integer, default=5))

    assert DefaultModel.__table__.c.score.default.arg == 5


def test_storage_spec_onupdate_callable():
    def incr(ctx):
        return 1

    class OnUpdateModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))
        updated = acol(storage=S(type_=Integer, onupdate=incr))

    assert OnUpdateModel.__table__.c.updated.onupdate.arg(None) == 1


def test_storage_spec_server_default():
    class ServerDefaultModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))
        created = acol(storage=S(type_=String, server_default=text("now()")))

    assert ServerDefaultModel.__table__.c.created.server_default.arg.text == "now()"


def test_storage_spec_comment():
    class CommentModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))
        note = acol(storage=S(type_=String, comment="hi"))

    assert CommentModel.__table__.c.note.comment == "hi"


def test_storage_spec_foreign_key():
    class Parent(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))

    class Child(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))
        parent_id = acol(
            storage=S(
                type_=Integer,
                fk=ForeignKeySpec(target="parent.id", on_delete="CASCADE"),
            )
        )

    fk = list(Child.__table__.c.parent_id.foreign_keys)[0]
    assert fk.column.table.name == "parent"
    assert fk.column.name == "id"
    assert fk.ondelete == "CASCADE"


def test_storage_spec_transform_to_stored():
    def upper(val, _ctx):
        return val.upper()

    spec = S(type_=String, transform=StorageTransform(to_stored=upper))

    assert spec.transform.to_stored("abc", None) == "ABC"


def test_storage_spec_refresh_on_return_preserved():
    spec = S(type_=Integer, primary_key=True, refresh_on_return=True)

    class RORModel(Base):
        id = acol(storage=spec)

    assert RORModel.__autoapi_cols__["id"].storage.refresh_on_return is True


def test_storage_spec_check_preserved():
    class CheckModel(Base):
        id = acol(storage=S(type_=Integer, primary_key=True))
        value = acol(storage=S(type_=Integer, check="value > 0"))

    assert CheckModel.__autoapi_cols__["value"].storage.check == "value > 0"
