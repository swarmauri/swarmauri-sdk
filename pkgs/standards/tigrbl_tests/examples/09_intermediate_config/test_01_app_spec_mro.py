from tigrbl.app.mro_collect import mro_collect_app_spec


def test_app_spec_mro_prefers_subclass():
    class BaseConfig:
        TITLE = "Base"
        JSONRPC_PREFIX = "/rpc"

    class ChildConfig(BaseConfig):
        TITLE = "Child"

    spec = mro_collect_app_spec(ChildConfig)
    assert spec.title == "Child"
    assert spec.jsonrpc_prefix == "/rpc"
