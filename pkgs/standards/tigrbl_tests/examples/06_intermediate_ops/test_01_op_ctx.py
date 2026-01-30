"""Lesson 06.1: Declaring context-only operations with `op_ctx`."""

from tigrbl import Base, TigrblApp, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_custom_op_ctx_registers_alias():
    """Explain how `op_ctx` contributes a discoverable alias.

    Purpose: demonstrate that custom operations can be attached without touching
    the canonical op list, while still appearing in the API registry.
    Design practice: always provide a stable alias so client integrations can
    depend on a predictable contract.
    """

    # Setup: define a minimal model with a required column.
    class LessonOp(Base, GUIDPk):
        __tablename__ = "lesson_ops"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    @op_ctx(alias="search", target="custom", arity="collection")
    def search(cls, ctx):
        return [{"name": "found"}]

    # Setup: attach the custom op to the model so the binder can discover it.
    LessonOp.search = search

    # Deployment: include the model in a TigrblApp and initialize bindings.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonOp)
    api.initialize()

    # Test: collect aliases from the app-bound OpSpecs.
    aliases = {spec.alias for spec in api.bind(LessonOp)}

    # Assertion: the custom alias appears in the bound operation set.
    assert "search" in aliases


def test_op_ctx_metadata_records_target_and_arity():
    """Show that op metadata captures intent for routing and docs.

    Purpose: verify the decorator records the target verb and arity so that
    downstream binders can generate the correct HTTP shape and RPC metadata.
    Design practice: make operation intent explicit to reduce implicit behavior.
    """

    # Setup: define a simple model so we can attach a custom operation.
    class LessonOpMeta(Base, GUIDPk):
        __tablename__ = "lesson_op_meta"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    @op_ctx(alias="summary", target="custom", arity="member")
    def summary(cls, ctx):
        return {"status": "ok"}

    # Setup: attach the operation to the model for declaration metadata.
    LessonOpMeta.summary = summary

    # Test: inspect the op declaration metadata on the underlying function.
    decl = LessonOpMeta.summary.__func__.__tigrbl_op_decl__

    # Assertion: the declaration retains alias, target, and arity intent.
    assert decl.alias == "summary"
    assert decl.target == "custom"
    assert decl.arity == "member"
