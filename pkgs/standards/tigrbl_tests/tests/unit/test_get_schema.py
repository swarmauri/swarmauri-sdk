import pytest

from tigrbl import get_schema
from tigrbl.bindings import build_schemas
from tigrbl.bindings.model import bind
from tigrbl.op import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base
from tigrbl.types import Column, String


def test_get_schema_returns_bound_request_and_response_from_bind():
    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_get_schema"
        name = Column(String, nullable=False)

    bind(Widget)

    assert get_schema(Widget, "create", kind="in") is Widget.schemas.create.in_
    assert get_schema(Widget, "create", kind="out") is Widget.schemas.create.out


def test_get_schema_kind_is_case_insensitive():
    class Gadget(Base, GUIDPk):
        __tablename__ = "gadgets_get_schema"
        name = Column(String, nullable=False)

    bind(Gadget)

    assert get_schema(Gadget, "create", kind="IN") is Gadget.schemas.create.in_


def test_get_schema_raises_for_unbound_model():
    class Unbound:
        pass

    with pytest.raises(KeyError):
        get_schema(Unbound, "create")


def test_get_schema_raises_for_unknown_op():
    class Gizmo(Base, GUIDPk):
        __tablename__ = "gizmos_get_schema"
        name = Column(String, nullable=False)

    spec = OpSpec(alias="create", target="create")
    build_schemas(Gizmo, [spec])

    with pytest.raises(KeyError):
        get_schema(Gizmo, "missing")


def test_get_schema_raises_for_invalid_kind():
    class Thing(Base, GUIDPk):
        __tablename__ = "things_get_schema"
        name = Column(String, nullable=False)

    spec = OpSpec(alias="create", target="create")
    build_schemas(Thing, [spec])

    with pytest.raises(ValueError):
        get_schema(Thing, "create", kind="sideways")


def test_get_schema_raises_when_kind_not_bound():
    class Custom(Base, GUIDPk):
        __tablename__ = "custom_get_schema"
        name = Column(String, nullable=False)

    spec = OpSpec(alias="ping", target="ping")
    build_schemas(Custom, [spec])

    with pytest.raises(KeyError):
        get_schema(Custom, "ping", kind="in")
