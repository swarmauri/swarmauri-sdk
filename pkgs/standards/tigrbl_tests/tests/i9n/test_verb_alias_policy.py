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

    router = create_test_api(AliasModelBoth)

    # Only the canonical verb is available.
    assert hasattr(router.core.AliasModelBoth, "create")
    assert not hasattr(router.core.AliasModelBoth, "register")
    assert hasattr(router.rpc.AliasModelBoth, "create")
    assert not hasattr(router.rpc.AliasModelBoth, "register")


@pytest.mark.i9n
def test_verb_alias_policy_canonical_only_blocks_alias(create_test_api) -> None:
    """Alias policy has no effect; aliases remain hidden."""

    class AliasModelBlocked(Base, GUIDPk):
        __tablename__ = "alias_model_blocked"
        __tigrbl_verb_aliases__ = {"create": "register"}
        __tigrbl_verb_alias_policy__ = "canonical_only"

    router = create_test_api(AliasModelBlocked)

    assert hasattr(router.core.AliasModelBlocked, "create")
    assert not hasattr(router.core.AliasModelBlocked, "register")
    assert hasattr(router.rpc.AliasModelBlocked, "create")
    assert not hasattr(router.rpc.AliasModelBlocked, "register")


@pytest.mark.i9n
def test_invalid_alias_is_ignored(create_test_api) -> None:
    """Invalid alias names are ignored without raising errors."""

    class BadAliasModel(Base, GUIDPk):
        __tablename__ = "bad_alias_model"
        __tigrbl_verb_aliases__ = {"create": "Bad-Name"}

    router = create_test_api(BadAliasModel)

    assert hasattr(router.core.BadAliasModel, "create")
    assert not hasattr(router.core.BadAliasModel, "Bad-Name")
    assert hasattr(router.rpc.BadAliasModel, "create")
    assert not hasattr(router.rpc.BadAliasModel, "Bad-Name")
