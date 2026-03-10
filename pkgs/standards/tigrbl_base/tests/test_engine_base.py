from tigrbl_base._base._engine_base import EngineBase


def test_engine_base_to_provider_not_implemented() -> None:
    engine = EngineBase()

    try:
        engine.to_provider()
    except NotImplementedError:
        assert True
    else:
        raise AssertionError("Expected NotImplementedError")
