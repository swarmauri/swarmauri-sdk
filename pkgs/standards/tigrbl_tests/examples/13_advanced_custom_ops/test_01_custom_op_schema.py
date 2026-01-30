from tigrbl import Base, SchemaRef, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_custom_op_declares_schema_refs():
    """Teach how custom ops reference schemas for request/response contracts.

    Purpose:
        Show that a custom op can declare explicit request/response schemas so
        clients get consistent validation and documentation.

    What this shows:
        - ``SchemaRef`` ties an op to named schema models.
        - The operation spec exposes request models after binding.

    Best practice:
        Always pair custom ops with explicit schema refs to keep API contracts
        stable and discoverable.
    """

    # Setup: declare a model with explicit columns.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_schema_widgets"
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

    # Setup: attach the custom op to the model.
    Widget.summarize = summarize

    # Deployment: include the model in an API and initialize schema wiring.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    api.initialize()

    # Test: bind and locate the custom op spec on the model.
    op = next(spec for spec in api.bind(Widget) if spec.alias == "summarize")

    # Assertion: the request schema is available for the operation.
    assert op.request_model is not None


def test_custom_op_schema_refs_cover_response_model():
    """Confirm custom ops expose response schemas in their specs.

    Purpose:
        Ensure that response schemas declared via ``SchemaRef`` are available
        on the operation spec for tooling and OpenAPI generation.

    What this shows:
        - Response models are built alongside request models.
        - Custom ops remain fully documented with typed outputs.

    Best practice:
        Use matching request/response schemas so RPC and REST clients can share
        consistent models.
    """

    # Setup: declare a new model for the response schema lesson.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_schema_response_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    @op_ctx(
        alias="describe",
        target="custom",
        arity="collection",
        request_schema=SchemaRef("create", "in"),
        response_schema=SchemaRef("read", "out"),
    )
    def describe(cls, ctx):
        return [{"name": "details"}]

    # Setup: attach the custom op to the model.
    Widget.describe = describe

    # Deployment: include the model in an API and initialize schema wiring.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    api.initialize()

    # Test: bind and locate the custom op spec on the model.
    op = next(spec for spec in api.bind(Widget) if spec.alias == "describe")

    # Assertion: the response schema is available for the operation.
    assert op.response_model is not None
