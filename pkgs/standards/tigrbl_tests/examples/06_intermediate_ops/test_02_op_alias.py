"""Lesson 06.2: Renaming canonical operations with `alias_ctx`."""

from tigrbl import Base, TigrblApp, alias, alias_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_alias_ctx_registers_custom_name():
    """Explain how aliasing exposes a custom verb without rewriting logic.

    Purpose: confirm that `alias_ctx` maps a canonical verb to a stable alias.
    Design practice: use aliases to keep APIs ergonomic while preserving core
    semantics (canonical target stays the same).
    """

    # Setup: define a model and apply an alias override for a canonical op.
    @alias_ctx(read="lookup")
    class LessonAlias(Base, GUIDPk):
        __tablename__ = "lesson_aliases"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: create an app and include the model so specs are bound.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonAlias)
    api.initialize()

    # Test: inspect the aliases produced by binding the model into the app.
    aliases = {spec.alias for spec in api.bind(LessonAlias)}

    # Assertion: the alias is present in the operation set.
    assert "lookup" in aliases


def test_alias_ctx_override_applies_arity():
    """Show that alias overrides can tune arity while keeping target stable.

    Purpose: demonstrate that override metadata (arity) is applied to the
    resolved OpSpec so routing can adapt without a custom handler.
    Design practice: prefer overrides for small behavioral changes instead of
    duplicating ops.
    """

    # Setup: define a model and override arity for the read verb alias.
    @alias_ctx(read=alias("peek", arity="member"))
    class LessonAliasOverride(Base, GUIDPk):
        __tablename__ = "lesson_alias_overrides"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind the model into an API so OpSpecs resolve with overrides.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonAliasOverride)
    api.initialize()

    # Test: find the bound spec with the overridden alias.
    spec = next(sp for sp in api.bind(LessonAliasOverride) if sp.alias == "peek")

    # Assertion: the alias keeps the canonical target but updates arity.
    assert spec.target == "read"
    assert spec.arity == "member"
