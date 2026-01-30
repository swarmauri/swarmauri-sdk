from tigrbl.orm.mixins import GUIDPk
from examples._support import build_widget_model


def test_guidpk_mixin_adds_id_column():
    Widget = build_widget_model("LessonMixin")
    assert hasattr(Widget, "id")
    assert issubclass(Widget, GUIDPk)
