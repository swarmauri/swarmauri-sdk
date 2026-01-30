from tigrbl import bind, build_schemas
from examples._support import build_widget_model


def test_build_schemas_returns_schema_map():
    Widget = build_widget_model("LessonSchemas")
    specs = bind(Widget)
    build_schemas(Widget, specs)
    assert hasattr(Widget, "schemas")
