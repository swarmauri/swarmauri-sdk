import pytest

from tigrbl import Base, TigrblApi
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_api_decl"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class WidgetApi(TigrblApi):
    PREFIX = "/widgets"
    TAGS = ("widgets",)
    MODELS = (Widget,)


@pytest.mark.unit
def test_tigrbl_api_subclass_declares_metadata() -> None:
    class_dir = dir(WidgetApi)

    assert "MODELS" in class_dir
    assert "TAGS" in class_dir
    assert "PREFIX" in class_dir
    assert WidgetApi.MODELS == (Widget,)
    assert WidgetApi.TAGS == ("widgets",)
    assert WidgetApi.PREFIX == "/widgets"
