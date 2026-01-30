"""Lesson 06.4: Understanding the default operation set."""

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_default_ops_include_list():
    """Show that default operation wiring includes collection listing.

    Purpose: verify the canonical "list" op is present when no overrides exist.
    Design practice: rely on defaults for standard CRUD to reduce boilerplate.
    """

    # Setup: declare a baseline model that uses only defaults.
    class LessonDefaultOps(Base, GUIDPk):
        __tablename__ = "lesson_default_ops"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: include the model in a Tigrbl app so ops are bound.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonDefaultOps)
    api.initialize()

    # Test: collect the aliases that the app binds for the model.
    aliases = {spec.alias for spec in api.bind(LessonDefaultOps)}

    # Assertion: the list operation is present by default.
    assert "list" in aliases


def test_default_ops_include_read_and_create():
    """Confirm multiple canonical ops are present out of the box.

    Purpose: reinforce that defaults cover read/create flows so custom code can
    focus on business-specific operations.
    Design practice: extend defaults only when necessary to keep APIs simple.
    """

    # Setup: define a model that relies on canonical defaults.
    class LessonDefaultOpsCore(Base, GUIDPk):
        __tablename__ = "lesson_default_ops_core"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    # Deployment: bind the model within an app context.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonDefaultOpsCore)
    api.initialize()

    # Test: read all bound aliases for the model.
    aliases = {spec.alias for spec in api.bind(LessonDefaultOpsCore)}

    # Assertion: core CRUD verbs are part of the default set.
    assert {"create", "read"}.issubset(aliases)
