import pytest

from tigrbl import TigrblApp, engine_ctx
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem


@pytest.mark.unit
def test_app_engine_param_registers_default_provider() -> None:
    _ = TigrblApp(engine=mem(async_=False))

    provider = _resolver.resolve_provider()
    assert provider is not None
    assert provider.spec.kind == "sqlite"
    assert provider.spec.async_ is False


@pytest.mark.unit
def test_app_engine_ctx_instance_requires_install_engines() -> None:
    app = TigrblApp()
    engine_ctx(mem(async_=False))(app)

    assert _resolver.resolve_provider() is None

    app.install_engines()
    provider = _resolver.resolve_provider()
    assert provider is not None
    assert provider.spec.kind == "sqlite"
