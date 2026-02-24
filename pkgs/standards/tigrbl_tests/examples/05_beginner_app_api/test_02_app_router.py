from tigrbl import Base, TigrblApp, TigrblRouter
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_app_router_registers_routes():
    """Verify that the API router is attached to the app.

    Purpose: show how the Tigrbl router becomes part of the app routing
    table, making model endpoints discoverable.

    Best practice: keep routing central and declarative so endpoints are easy
    to audit and document.
    """

    # Setup: define a model and initialize a Tigrbl API.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonrouter"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

<<<<<<< HEAD
    app = TigrblApp(engine=mem(async_=False))
    # Deployment: include the model and initialize to generate routes.
    app.include_table(Widget)
    app.initialize()
    # Deployment: mount the Tigrbl router on an app.
    router = TigrblRouter()
    app.include_router(router)
=======
    router = TigrblApp(engine=mem(async_=False))
    # Deployment: include the model and initialize to generate routes.
    router.include_model(Widget)
    router.initialize()
    # Deployment: mount the Tigrbl router on a FastAPI app.
    app = TigrblApp()
    app.include_router(router.router)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    # Exercise: list registered paths.
    routes = {route.path for route in app.router.routes}
    # Assertion: the model route exists for the widget resource.
    assert f"/{Widget.__name__.lower()}" in routes


def test_app_router_contains_model_route_once():
    """Confirm the model route is registered exactly once.

    Purpose: prevent accidental duplicate route registrations that could cause
    ambiguous routing or unexpected handler execution.

    Best practice: initialize routers in a single place to avoid duplicate
    route inclusion.
    """

    # Setup: declare another model and API for a clean route table.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonroutersingle"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

<<<<<<< HEAD
    app = TigrblApp(engine=mem(async_=False))
    # Deployment: include the model, initialize, and mount on an app.
    app.include_table(Widget)
    app.initialize()
    router = TigrblRouter()
    app.include_router(router)
=======
    router = TigrblApp(engine=mem(async_=False))
    # Deployment: include the model, initialize, and mount on a FastAPI app.
    router.include_model(Widget)
    router.initialize()
    app = TigrblApp()
    app.include_router(router.router)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    # Exercise: collect route entries for the model path.
    model_path = f"/{Widget.__name__.lower()}"
    model_routes = [route for route in app.router.routes if route.path == model_path]
    # Assertion: the path exists and is shared across multiple methods.
    assert model_routes
    assert {method for route in model_routes for method in route.methods} >= {
        "GET",
        "POST",
    }
