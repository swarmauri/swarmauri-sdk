from tigrbl_base._base._engine_provider_base import EngineProviderBase


class ProviderImpl:
    spec = {"name": "sqlite"}

    def to_provider(self) -> "ProviderImpl":
        return self


def test_engine_provider_protocol_runtime_checkable() -> None:
    provider = ProviderImpl()
    assert isinstance(provider, EngineProviderBase)
