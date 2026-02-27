from tigrbl.table.mro_collect import mro_collect_table_spec
from tigrbl.table.shortcuts import defineTableSpec


class BaseSpec(defineTableSpec(engine="sqlite://:memory:", ops=("create",))):
    __tablename__ = "widgets"


class Widget(BaseSpec):
    OPS = ("read",)
    COLUMNS = ("id", "name")


class ConcreteSpecBase(defineTableSpec(engine="sqlite:///:memory:", ops=("create",))):
    __tablename__ = "widgets_concrete"


class ConcreteWidget(ConcreteSpecBase):
    OPS = ("read",)


def test_table_spec_defaults_and_merge():
    spec = mro_collect_table_spec(Widget)
    assert spec.model is Widget
    assert spec.engine == "sqlite://:memory:"
    assert spec.ops == ("read", "create")
    assert spec.columns == ("id", "name")
    assert spec.schemas == ()
    assert spec.hooks == ()


def test_concrete_table_initializes_from_mro_collect_spec():
    assert ConcreteWidget.OPS == ("read", "create")
    assert ConcreteWidget.table_config["engine"] == "sqlite:///:memory:"
