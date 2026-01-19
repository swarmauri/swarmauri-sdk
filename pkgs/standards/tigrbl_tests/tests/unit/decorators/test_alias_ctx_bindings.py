from tigrbl import App, alias, alias_ctx


def test_alias_ctx_internal_binding_on_model_class():
    @alias_ctx(read="fetch")
    class Widget:
        pass

    assert Widget.__tigrbl_aliases__["read"] == "fetch"
    assert "read" not in Widget.__tigrbl_alias_overrides__


def test_alias_ctx_external_binding_on_model_class_with_overrides():
    class Gadget:
        pass

    decorator = alias_ctx(create=alias("register", persist="skip"))
    bound = decorator(Gadget)

    assert bound is Gadget
    assert Gadget.__tigrbl_aliases__["create"] == "register"
    overrides = Gadget.__tigrbl_alias_overrides__["create"]
    assert overrides["persist"] == "skip"


def test_alias_ctx_binding_on_app_class_retains_alias_mapping():
    class ExampleApp(App):
        pass

    alias_ctx(delete="remove")(ExampleApp)

    assert ExampleApp.__tigrbl_aliases__["delete"] == "remove"
    # App classes do not participate in op collection; ensure override map exists but empty.
    assert ExampleApp.__tigrbl_alias_overrides__ == {}
