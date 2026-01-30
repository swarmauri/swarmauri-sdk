from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_engine_precedence_resolves_latest_on_model():
    """Explain how model-level engine config takes precedence in the API.

    Purpose:
        Show that when a child model overrides engine configuration, the API
        records the child's engine binding after inclusion.

    What this shows:
        - Model inheritance can override ``table_config`` values.
        - The API exposes the resolved config in ``api.table_config``.

    Best practice:
        Keep engine decisions on the most specific model to avoid ambiguity in
        multi-tenant or multi-database deployments.
    """

    base_engine = mem(async_=False)
    child_engine = mem(async_=False)

    # Setup: define a base mixin with a default engine binding.
    class BaseWidgetMixin:
        table_config = {"engine": base_engine}

    # Setup: define the concrete model and override the engine binding.
    class ChildWidget(BaseWidgetMixin, Base, GUIDPk):
        __tablename__ = "engine_child_widgets"
        __allow_unmapped__ = True
        table_config = {"engine": child_engine}
        name = Column(String, nullable=False)

    # Deployment: include the child model in a Tigrbl app.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(ChildWidget)

    # Test: the API stores the child's engine config, not the base's.
    config = api.table_config[ChildWidget.__name__]

    # Assertion: the engine reference matches the child override.
    assert config["engine"] is child_engine
