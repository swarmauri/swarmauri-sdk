from tigrbl.app.mro_collect import mro_collect_app_spec


def test_prefix_precedence_overrides_parent():
    class BaseConfig:
        SYSTEM_PREFIX = "/system"

    class ChildConfig(BaseConfig):
        SYSTEM_PREFIX = "/systemz"

    spec = mro_collect_app_spec(ChildConfig)
    assert spec.system_prefix == "/systemz"
