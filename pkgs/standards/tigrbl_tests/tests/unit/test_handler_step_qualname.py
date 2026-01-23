from tigrbl.bindings.handlers import build_and_attach
from tigrbl.op import OpSpec
from tigrbl import core as _core


def test_wrap_core_preserves_qualname_and_module():
    class Model:
        pass

    sp = OpSpec(alias="create", target="create")
    build_and_attach(Model, [sp])

    step = Model.hooks.create.HANDLER[0]
    assert step.__qualname__ == _core.create.__qualname__
    assert step.__module__ == _core.create.__module__


def test_wrap_custom_preserves_qualname_and_module():
    class Model:
        pass

    def custom_handler(ctx):
        return None

    sp = OpSpec(alias="custom", target="custom", handler=custom_handler)
    build_and_attach(Model, [sp])

    step = Model.hooks.custom.HANDLER[0]
    assert step.__qualname__ == custom_handler.__qualname__
    assert step.__module__ == custom_handler.__module__
