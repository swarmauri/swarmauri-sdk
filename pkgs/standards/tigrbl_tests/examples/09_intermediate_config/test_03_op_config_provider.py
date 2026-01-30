from tigrbl.types import OpConfigProvider


def test_op_config_provider_defaults_mode():
    class LessonOpProvider(OpConfigProvider):
        __tigrbl_defaults_mode__ = "none"

    assert LessonOpProvider.__tigrbl_defaults_mode__ == "none"
