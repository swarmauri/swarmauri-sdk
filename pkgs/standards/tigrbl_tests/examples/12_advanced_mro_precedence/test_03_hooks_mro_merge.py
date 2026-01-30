from tigrbl.app.mro_collect import mro_collect_app_spec


def test_hook_sequence_merges_across_mro():
    class BaseConfig:
        HOOKS = ("base",)

    class ChildConfig(BaseConfig):
        HOOKS = ("child",)

    spec = mro_collect_app_spec(ChildConfig)
    assert spec.hooks == ("base", "child")
