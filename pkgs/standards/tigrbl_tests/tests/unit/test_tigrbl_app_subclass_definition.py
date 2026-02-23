import pytest

from tigrbl import Base, TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import Mapped, String


class Widget(Base, GUIDPk):
    __tablename__ = "widgets_app_decl"
    __allow_unmapped__ = True

    name: Mapped[str] = acol(
        storage=S(type_=String, nullable=False),
        field=F(py_type=str),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    __tigrbl_cols__ = {"id": GUIDPk.id, "name": name}


class WidgetApp(TigrblApp):
    TITLE = "Widget App"
    VERSION = "1.0.0"
    MODELS = (Widget,)


@pytest.mark.unit
def test_tigrbl_app_subclass_declares_metadata() -> None:
    class_dir = dir(WidgetApp)

    assert "TITLE" in class_dir
    assert "VERSION" in class_dir
    assert "MODELS" in class_dir
    assert WidgetApp.TITLE == "Widget App"
    assert WidgetApp.VERSION == "1.0.0"
    assert WidgetApp.MODELS == (Widget,)
