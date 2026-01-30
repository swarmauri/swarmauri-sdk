from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_default_ops_register_core_verbs():
    """Confirm the core CRUD verbs are registered by default.

    Purpose: show that the standard operation set is ready without extra
    configuration once a model is included.

    Best practice: verify core verbs early so customizations do not remove
    essential operations unintentionally.
    """

    # Setup: define a model and initialize a Tigrbl API.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonops"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    api = TigrblApp(engine=mem(async_=False))
    # Deployment: include the model and initialize default operations.
    api.include_model(Widget)
    api.initialize()
    # Exercise: gather the operation aliases bound to the model.
    verbs = {spec.alias for spec in api.bind(Widget)}
    # Assertion: core CRUD verbs are present by default.
    assert {"create", "read", "update", "delete", "list"}.issubset(verbs)


def test_default_ops_are_exposed_as_aliases():
    """Demonstrate that operation specs expose consistent aliases.

    Purpose: teach how to introspect operation bindings for documentation or
    client generation workflows.

    Best practice: rely on stable aliases to reduce churn in API clients.
    """

    # Setup: define a model and API for alias inspection.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonopsaliases"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    api = TigrblApp(engine=mem(async_=False))
    # Deployment: include the model and initialize operations.
    api.include_model(Widget)
    api.initialize()
    # Exercise: list bound operation aliases.
    aliases = {spec.alias for spec in api.bind(Widget)}
    # Assertion: common aliases like create/list are always available.
    assert "create" in aliases
    assert "list" in aliases
