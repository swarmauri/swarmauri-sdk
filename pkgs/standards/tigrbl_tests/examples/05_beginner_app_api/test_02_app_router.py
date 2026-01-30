from examples._support import (
    build_fastapi_app,
    build_simple_api,
    build_widget_model,
    model_route,
)


def test_app_router_registers_routes():
    Widget = build_widget_model("LessonRouter")
    api = build_simple_api(Widget)
    app = build_fastapi_app(api)
    routes = {route.path for route in app.router.routes}
    assert model_route(Widget) in routes
