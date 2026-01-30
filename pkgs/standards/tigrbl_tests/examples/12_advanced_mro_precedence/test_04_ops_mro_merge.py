from tigrbl import Base, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_ops_precedence_prefers_child_override():
    """Explain operation precedence when child models override base ops.

    Purpose:
        Show that if a child model declares an op with the same name as the
        base model, the child declaration wins after API binding.

    What this shows:
        - Operation decorators are collected across the MRO.
        - Child ops override base ops with the same name.

    Best practice:
        Override ops only when behavior must change; keep base ops stable to
        preserve consistent APIs.
    """

    # Setup: define a base mixin with a recognizable status code.
    class BaseWidgetMixin:
        @op_ctx(alias="report", target="custom", arity="collection", status_code=200)
        def report(cls, ctx):
            return [{"report": "base"}]

    # Setup: define a concrete model that overrides the op definition.
    class ChildWidget(BaseWidgetMixin, Base, GUIDPk):
        __tablename__ = "ops_child_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

        @op_ctx(alias="report", target="custom", arity="collection", status_code=201)
        def report(cls, ctx):
            return [{"report": "child"}]

    # Deployment: include the child model on the API (composition step).
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(ChildWidget)

    # Test: request the bound op specs from the API.
    specs = api.bind(ChildWidget)

    # Test: find the custom op spec for the report alias.
    report_spec = next(spec for spec in specs if spec.alias == "report")

    # Assertion: the child op definition wins, carrying the child status code.
    assert report_spec.status_code == 201
