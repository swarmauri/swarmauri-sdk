from __future__ import annotations

import pytest

from tigrbl_core._spec.alias_spec import AliasSpec


class MinimalAlias(AliasSpec):
    @property
    def alias(self) -> str:
        return "alias"

    @property
    def request_schema(self):
        return None

    @property
    def response_schema(self):
        return None

    @property
    def persist(self):
        return "default"

    @property
    def arity(self):
        return "collection"

    @property
    def rest(self):
        return True


def test_alias_spec_is_abstract() -> None:
    with pytest.raises(TypeError):
        AliasSpec()


def test_alias_spec_concrete_implementation_returns_contract_values() -> None:
    spec = MinimalAlias()

    assert spec.alias == "alias"
    assert spec.request_schema is None
    assert spec.response_schema is None
    assert spec.persist == "default"
    assert spec.arity == "collection"
    assert spec.rest is True
