from autoapi.v3.bindings.model import bind
from autoapi.v3.tables import Base
from autoapi.v3.specs import acol, vcol, S, F, IO
from autoapi.v3.types import Integer, String
from pydantic import BaseModel


class Widget(Base):
    __tablename__ = "widgets"
    __allow_unmapped__ = True

    id: int = acol(
        storage=S(type_=Integer, primary_key=True, nullable=False),
        io=IO(out_verbs=("read", "list")),
    )
    name: str = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str, constraints={"min_length": 1}),
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )
    token: str = vcol(
        field=F(py_type=str),
        io=IO(in_verbs=("create",)),
        default_factory=lambda ctx: "tok",
    )
    greeting: str = vcol(
        field=F(py_type=str),
        io=IO(out_verbs=("read",)),
        read_producer=lambda obj, ctx: f"hi {obj.name}",
    )


bind(Widget)


def test_openapi_schemas_and_bindings():
    # request schema should be attached for create operations
    assert hasattr(Widget.schemas, "create")
    assert issubclass(Widget.schemas.create.in_, BaseModel)

    # response schema should be attached for read operations
    assert hasattr(Widget.schemas, "read")
    assert issubclass(Widget.schemas.read.out, BaseModel)

    # persisted columns should be present on the table; virtual ones should not
    assert set(Widget.__table__.columns.keys()) == {"id", "name"}
    assert set(Widget.__autoapi_cols__.keys()) == {"id", "name", "token", "greeting"}

    # canonical ops should be bound on the model
    expected_ops = {"create", "read", "update", "replace", "delete", "list"}
    assert expected_ops <= set(Widget.opspecs.by_alias.keys())
