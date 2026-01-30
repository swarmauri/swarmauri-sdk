from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_model_resource_precedence_overrides_base():
    """Explain how model resource names follow MRO overrides.

    Purpose:
        Demonstrate that a child model can override ``__resource__`` and the API
        will expose the child resource name when the model is included.

    What this shows:
        - Model-level routing names follow inheritance precedence.
        - The API exposes resource-based RPC namespaces derived from models.

    Best practice:
        Override ``__resource__`` on the most specific model to keep resource
        naming intentional and clear.
    """

    # Setup: define a base mixin with a resource name.
    class BaseWidgetMixin:
        __resource__ = "base_widget"

    # Setup: define the concrete model and override the resource name.
    class ChildWidget(BaseWidgetMixin, Base, GUIDPk):
        __tablename__ = "resource_child_widgets"
        __allow_unmapped__ = True
        __resource__ = "child_widget"
        name = Column(String, nullable=False)

    # Deployment: include the child model in an API.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(ChildWidget)

    # Test: the API router paths use the child resource name.
    router = api.routers[ChildWidget.__name__]
    paths = {route.path for route in router.routes}

    # Assertion: the REST paths include the child resource segment.
    assert any(path.startswith("/child_widget") for path in paths)
