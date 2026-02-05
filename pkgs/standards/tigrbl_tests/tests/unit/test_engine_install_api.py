import pytest

from tigrbl import TigrblApi, engine_ctx
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem


@pytest.mark.unit
def test_api_engine_param_registers_api_provider() -> None:
    api = TigrblApi(engine=mem(async_=False))

    provider = _resolver.resolve_provider(api=api)
    assert provider is not None
    assert provider.spec.kind == "sqlite"
    assert provider.spec.async_ is False


@pytest.mark.unit
def test_api_engine_ctx_instance_requires_install_engines() -> None:
    api = TigrblApi()
    engine_ctx(mem(async_=False))(api)

    assert _resolver.resolve_provider(api=api) is None

    api.install_engines(api=api)
    provider = _resolver.resolve_provider(api=api)
    assert provider is not None
    assert provider.spec.kind == "sqlite"
