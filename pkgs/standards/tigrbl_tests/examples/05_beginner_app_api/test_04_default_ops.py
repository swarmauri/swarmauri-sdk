from examples._support import build_simple_api, build_widget_model


def test_default_ops_register_core_verbs():
    Widget = build_widget_model("LessonOps")
    api = build_simple_api(Widget)
    verbs = {spec.alias for spec in api.bind(Widget)}
    assert {"create", "read", "update", "delete", "list"}.issubset(verbs)
