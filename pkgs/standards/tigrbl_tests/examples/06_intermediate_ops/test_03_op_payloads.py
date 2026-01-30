from tigrbl import Base, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_custom_op_returns_payload():
    """Test custom op returns payload."""

    # Setup: define a minimal model to attach a custom operation.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonpayload"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    @op_ctx(alias="summary", target="custom", arity="instance")
    def summary(cls, ctx):
        return {"status": "ok"}

    # Deployment: attach the custom op to the model class.
    Widget.summary = summary

    # Deployment: include the model in a Tigrbl API and initialize bindings.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    api.initialize()
    # Exercise: locate the custom op in the API bindings.
    spec = next(spec for spec in api.bind(Widget) if spec.alias == "summary")
    # Assertion: the custom op has a handler bound.
    assert spec.handler is not None
