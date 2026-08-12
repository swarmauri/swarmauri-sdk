from collections.abc import Mapping

import pytest

from swarmauri_core.model_providers import IProviderAuth, IProviderEndpoint


def test_provider_auth_requires_apply() -> None:
    class IncompleteAuth(IProviderAuth):
        pass

    with pytest.raises(TypeError):
        IncompleteAuth()


def test_provider_endpoint_requires_resolve() -> None:
    class IncompleteEndpoint(IProviderEndpoint):
        pass

    with pytest.raises(TypeError):
        IncompleteEndpoint()


def test_complete_contracts_are_instantiable() -> None:
    class Auth(IProviderAuth):
        def apply(self, headers: Mapping[str, str]) -> Mapping[str, str]:
            return headers

        def apply_query(self, query: Mapping[str, str]) -> Mapping[str, str]:
            return query

    class Endpoint(IProviderEndpoint):
        def resolve(self, capability: str) -> str:
            return f"https://example.test/{capability}"

    assert Auth().apply({"Accept": "application/json"}) == {
        "Accept": "application/json"
    }
    assert Endpoint().resolve("models.list").endswith("/models.list")
