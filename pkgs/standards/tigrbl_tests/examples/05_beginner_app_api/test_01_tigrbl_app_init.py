from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_app_includes_model_and_registry():
    """Ensure a model is registered when included in the app.

    Purpose: illustrate the app lifecycle—include the model, initialize the
    app, then query the registry to confirm the model is active.

    Best practice: initialize once and re-use the app instance to keep routing
    and dependency wiring deterministic.
    """

    # Setup: define a model and a Tigrbl API instance.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonapi"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    api = TigrblApp(engine=mem(async_=False))
    # Deployment: include the model and initialize the API.
    api.include_model(Widget)
    api.initialize()
    # Exercise: retrieve the model registry entry.
    registry = api.registry(Widget)
    # Assertion: the registry entry exists after initialization.
    assert registry is not None


def test_app_model_map_tracks_the_model_class():
    """Show that the app retains a model lookup table.

    Purpose: verify that the app keeps a registry of models that can be used by
    tooling, documentation, and diagnostics.

    Best practice: centralize model registration so downstream integrations can
    enumerate enabled resources reliably.
    """

    # Setup: declare a model and API instance.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonapiregistry"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    api = TigrblApp(engine=mem(async_=False))
    # Deployment: include and initialize so the model map is populated.
    api.include_model(Widget)
    api.initialize()
    # Assertion: the model registry maps the class name to the model class.
    assert api.models[Widget.__name__] is Widget
