import pytest

from tigrbl import TigrblRouter, engine_ctx
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem


@pytest.mark.unit
def test_api_engine_param_registers_api_provider() -> None:
    router = TigrblRouter(engine=mem(async_=False))

    provider = _resolver.resolve_provider(api=router)
    assert provider is not None
    assert provider.spec.kind == "sqlite"
    assert provider.spec.async_ is False


@pytest.mark.unit
def test_api_engine_ctx_instance_requires_install_engines() -> None:
    router = TigrblRouter()
    engine_ctx(mem(async_=False))(router)

    assert _resolver.resolve_provider(api=router) is None

    router.install_engines(api=router)
    provider = _resolver.resolve_provider(api=router)
    assert provider is not None
    assert provider.spec.kind == "sqlite"
