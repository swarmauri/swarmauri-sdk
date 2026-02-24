from tigrbl.engine import resolver
from tigrbl.engine.shortcuts import mem


def _reset_resolver_state() -> None:
    resolver.reset(dispose=True)


def test_interns_providers_by_engine_spec() -> None:
    _reset_resolver_state()

    class Api:
        pass

    class Model:
        pass

    cfg = mem(async_=False)
    resolver.set_default(cfg)
    resolver.register_router(Api, cfg)
    resolver.register_table(Model, cfg)
    resolver.register_op(Model, "create", cfg)

    p_default = resolver.resolve_provider()
<<<<<<< HEAD
    p_router = resolver.resolve_provider(router=Api())
=======
    p_api = resolver.resolve_provider(router=Api())
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    p_model = resolver.resolve_provider(model=Model)
    p_op = resolver.resolve_provider(model=Model, op_alias="create")

    assert p_default is p_router is p_model is p_op

    _reset_resolver_state()


def test_warmup_builds_all_registered_providers() -> None:
    _reset_resolver_state()

    class Api:
        pass

    cfg = mem(async_=False)
    resolver.set_default(cfg)
    resolver.register_router(Api, cfg)

    providers = resolver.iter_providers()
    assert len(providers) == 1
    assert providers[0]._maker is None

    resolver.warmup()

    providers = resolver.iter_providers()
    assert len(providers) == 1
    assert providers[0]._maker is not None

    _reset_resolver_state()
