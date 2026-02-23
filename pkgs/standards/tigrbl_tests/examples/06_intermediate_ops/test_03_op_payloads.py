"""Lesson 06.3: Verifying payload handlers for custom operations."""

from tigrbl import Base, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_custom_op_returns_payload():
    """Validate that custom ops bind to handlers that return payloads.

    Purpose: show that a ctx-only handler is captured by OpSpec resolution,
    enabling custom payloads without modifying core CRUD behavior.
    Design practice: keep custom handlers focused and return explicit payloads
    for clear API contracts.
    """

    # Setup: declare a model with a column so bindings can materialize.
    class LessonPayload(Base, GUIDPk):
        __tablename__ = "lesson_payloads"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    @op_ctx(alias="summary", target="custom", arity="member")
    def summary(cls, ctx):
        return {"status": "ok"}

    # Setup: attach the custom op so it can be bound.
    LessonPayload.summary = summary

    # Deployment: build an app and include the model so OpSpecs resolve.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonPayload)
    api.initialize()

    # Test: locate the OpSpec for the custom alias on the bound model.
    spec = next(sp for sp in api.bind(LessonPayload) if sp.alias == "summary")

    # Assertion: the custom op has a handler attached.
    assert spec.handler is not None


def test_custom_op_exposes_target_and_handler():
    """Confirm OpSpec exposes the handler and custom target pairing.

    Purpose: ensure the resolved OpSpec retains the custom target so binders can
    differentiate between canonical and bespoke operations.
    Design practice: inspect OpSpecs when debugging to verify behavior early.
    """

    # Setup: declare a model to bind a custom operation against.
    class LessonPayloadMeta(Base, GUIDPk):
        __tablename__ = "lesson_payload_meta"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    @op_ctx(alias="describe", target="custom", arity="collection")
    def describe(cls, ctx):
        return [{"name": "alpha"}]

    # Setup: attach the custom op so the binder can register it.
    LessonPayloadMeta.describe = describe

    # Deployment: create an app, include the model, and initialize bindings.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonPayloadMeta)
    api.initialize()

    # Test: pull the spec from the bound model set.
    spec = next(sp for sp in api.bind(LessonPayloadMeta) if sp.alias == "describe")

    # Assertion: the spec advertises the custom target and a handler.
    assert spec.target == "custom"
    assert spec.handler is not None
