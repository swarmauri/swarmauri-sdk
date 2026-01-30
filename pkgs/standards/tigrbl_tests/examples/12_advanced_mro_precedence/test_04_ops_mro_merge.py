from tigrbl.app.mro_collect import mro_collect_app_spec


def test_ops_sequence_merges_across_mro():
    class BaseConfig:
        OPS = ("base",)

    class ChildConfig(BaseConfig):
        OPS = ("child",)

    spec = mro_collect_app_spec(ChildConfig)
    assert spec.ops == ("base", "child")
