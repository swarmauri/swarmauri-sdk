"""Tests for Tigrbl verb alias configuration (currently ignored)."""

import pytest

from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk


@pytest.mark.i9n
def test_verb_alias_policy_both_routes_same_handler(create_test_api) -> None:
    """Verb aliases are ignored; only canonical verbs are exposed."""

    class AliasModelBoth(Base, GUIDPk):
        __tablename__ = "alias_model"
        __tigrbl_verb_aliases__ = {"create": "register"}
        __tigrbl_verb_alias_policy__ = "both"

    api = create_test_api(AliasModelBoth)

    # Only the canonical verb is available.
    assert hasattr(api.core.AliasModelBoth, "create")
    assert not hasattr(api.core.AliasModelBoth, "register")
    assert hasattr(api.rpc.AliasModelBoth, "create")
    assert not hasattr(api.rpc.AliasModelBoth, "register")


@pytest.mark.i9n
def test_verb_alias_policy_canonical_only_blocks_alias(create_test_api) -> None:
    """Alias policy has no effect; aliases remain hidden."""

    class AliasModelBlocked(Base, GUIDPk):
        __tablename__ = "alias_model_blocked"
        __tigrbl_verb_aliases__ = {"create": "register"}
        __tigrbl_verb_alias_policy__ = "canonical_only"

    api = create_test_api(AliasModelBlocked)

    assert hasattr(api.core.AliasModelBlocked, "create")
    assert not hasattr(api.core.AliasModelBlocked, "register")
    assert hasattr(api.rpc.AliasModelBlocked, "create")
    assert not hasattr(api.rpc.AliasModelBlocked, "register")


@pytest.mark.i9n
def test_invalid_alias_is_ignored(create_test_api) -> None:
    """Invalid alias names are ignored without raising errors."""

    class BadAliasModel(Base, GUIDPk):
        __tablename__ = "bad_alias_model"
        __tigrbl_verb_aliases__ = {"create": "Bad-Name"}

    api = create_test_api(BadAliasModel)

    assert hasattr(api.core.BadAliasModel, "create")
    assert not hasattr(api.core.BadAliasModel, "Bad-Name")
    assert hasattr(api.rpc.BadAliasModel, "create")
    assert not hasattr(api.rpc.BadAliasModel, "Bad-Name")
