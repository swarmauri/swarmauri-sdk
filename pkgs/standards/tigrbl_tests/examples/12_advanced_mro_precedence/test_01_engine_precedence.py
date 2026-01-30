from tigrbl.app.mro_collect import mro_collect_app_spec
from tigrbl.engine.shortcuts import mem


def test_engine_precedence_resolves_latest():
    """Test engine precedence resolves latest."""

    class BaseConfig:
        ENGINE = mem(async_=False)

    class ChildConfig(BaseConfig):
        ENGINE = mem(async_=False)

    spec = mro_collect_app_spec(ChildConfig)
    assert spec.engine is not None
