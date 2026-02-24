from types import SimpleNamespace

from tigrbl.specs import F, S, acol
from tigrbl.table import Table
from tigrbl.types import Integer, Mapped


class BaseWidget(Table):
    __abstract__ = True

    id: Mapped[int] = acol(
        storage=S(type_=Integer, primary_key=True), field=F(py_type=int)
    )


class WidgetAlpha(BaseWidget):
    __tablename__ = "widgets_namespace_alpha"


class WidgetBeta(BaseWidget):
    __tablename__ = "widgets_namespace_beta"


def test_model_namespaces_are_per_class() -> None:
    assert isinstance(WidgetAlpha.ops, SimpleNamespace)
    assert isinstance(WidgetBeta.ops, SimpleNamespace)
    assert WidgetAlpha.ops is WidgetAlpha.opspecs
    assert WidgetBeta.ops is WidgetBeta.opspecs
    assert WidgetAlpha.ops is not WidgetBeta.ops
    assert WidgetAlpha.schemas is not WidgetBeta.schemas
    assert WidgetAlpha.hooks is not WidgetBeta.hooks
    assert WidgetAlpha.handlers is not WidgetBeta.handlers
    assert WidgetAlpha.rpc is not WidgetBeta.rpc
    assert WidgetAlpha.rest is not WidgetBeta.rest
    assert WidgetAlpha.__tigrbl_hooks__ is not WidgetBeta.__tigrbl_hooks__


def test_model_namespace_mutations_do_not_bleed() -> None:
    WidgetAlpha.ops.by_alias["alpha_only"] = ["alpha"]
    assert "alpha_only" not in WidgetBeta.ops.by_alias

    WidgetAlpha.schemas.alpha_only = "alpha_schema"
    assert not hasattr(WidgetBeta.schemas, "alpha_only")
