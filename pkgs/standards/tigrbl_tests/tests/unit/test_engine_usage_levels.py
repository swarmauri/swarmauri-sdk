from tigrbl.engine import resolver
from tigrbl.engine.shortcuts import mem


def test_engine_usage_levels_and_precedence():
    # Start from a clean registry to avoid cross-test pollution
    resolver.set_default(None)
    resolver._API.clear()
    resolver._TAB.clear()
    resolver._OP.clear()

    class Api:
        pass

    class Model:
        __name__ = "Model"

    resolver.set_default(mem(async_=False))
    resolver.register_api(Api, mem(async_=True))
    resolver.register_table(Model, mem(async_=False))
    resolver.register_op(Model, "create", mem(async_=True))

    api_inst = Api()
    model_inst = Model()

    p = resolver.resolve_provider(api=api_inst, model=model_inst, op_alias="create")
    assert p is not None and p.spec.async_ is True

    p_model = resolver.resolve_provider(api=api_inst, model=model_inst)
    assert p_model is not None and p_model.spec.async_ is False

    p_api = resolver.resolve_provider(api=api_inst)
    assert p_api is not None and p_api.spec.async_ is True

    p_default = resolver.resolve_provider()
    assert p_default is not None and p_default.spec.async_ is False
