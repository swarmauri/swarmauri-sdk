from tigrbl import Base, SchemaRef, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_custom_op_declares_schema_refs():
    """Test custom op declares schema refs."""

    # Setup: define a model to host a custom collection op.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonschema"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    @op_ctx(
        alias="summarize",
        target="custom",
        arity="collection",
        request_schema=SchemaRef("create", "in"),
        response_schema=SchemaRef("read", "out"),
    )
    def summarize(cls, ctx):
        return [{"name": "summary"}]

    # Deployment: attach the custom op to the model class.
    Widget.summarize = summarize

    # Deployment: include the model on a Tigrbl API and initialize.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    api.initialize()
    # Exercise: locate the summarized operation in the bound ops.
    op = next(spec for spec in api.bind(Widget) if spec.alias == "summarize")
    # Assertion: request schemas are resolved for the op.
    assert op.request_model is not None
