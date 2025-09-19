from tigrbl import App, op_alias


def _latest_spec(obj):
    return obj.__tigrbl_ops__[-1]


def test_op_alias_internal_binding_on_model_class():
    @op_alias(alias="fetch", target="read")
    class Widget:
        pass

    spec = _latest_spec(Widget)
    assert spec.alias == "fetch"
    assert spec.target == "read"
    assert spec.table is Widget


def test_op_alias_external_binding_on_model_class():
    class Gadget:
        pass

    op_alias(alias="search", target="custom", http_methods=("POST",))(Gadget)

    spec = _latest_spec(Gadget)
    assert spec.alias == "search"
    assert spec.http_methods == ("POST",)
    assert spec.table is Gadget


def test_op_alias_binding_on_app_class_stores_spec_for_reference():
    class ExampleApp(App):
        pass

    op_alias(alias="diagnostics", target="custom")(ExampleApp)

    spec = _latest_spec(ExampleApp)
    assert spec.alias == "diagnostics"
    assert spec.table is ExampleApp
