from tigrbl.orm.tables._base import _materialize_colspecs_to_sqla
from tigrbl.specs import acol, S, F, IO
from tigrbl.types import Integer, String
from tigrbl.schema import _build_list_params
from sqlalchemy.orm import Mapped, DeclarativeBase


class LocalBase(DeclarativeBase):
    def __init_subclass__(cls, **kw):  # pragma: no cover - simple mapper hook
        _materialize_colspecs_to_sqla(cls)
        super().__init_subclass__(**kw)


class Thing(LocalBase):
    __tablename__ = "spec_things"

    id: Mapped[int] = acol(
        storage=S(type_=Integer, primary_key=True),
        field=F(py_type=int),
        io=IO(out_verbs=("read", "list")),
    )
    name: Mapped[str] = acol(
        storage=S(type_=String),
        field=F(py_type=str),
        io=IO(out_verbs=("read", "list"), filter_ops=("eq", "like")),
    )


def test_build_list_params_with_spec_only_model():
    params = _build_list_params(Thing)
    fields = set(params.model_fields.keys())
    assert "name" in fields
    assert "name__like" in fields
