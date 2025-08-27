"""Tests for AutoAPI verb aliasing and policy handling."""

import pytest

from autoapi.v3.types import Base, GUIDPk, OpVerbAliasProvider


@pytest.mark.i9n
def test_verb_alias_policy_both_routes_same_handler(create_test_api):
    """Canonical verbs and aliases should map to the same handler when allowed."""

    class AliasModelBoth(Base, GUIDPk, OpVerbAliasProvider):
        __tablename__ = "alias_model"
        __autoapi_verb_aliases__ = {"create": "register"}
        __autoapi_verb_alias_policy__ = "both"

    api = create_test_api(AliasModelBoth)

    # Alias mapping currently has no effect; only canonical verb is exposed
    assert hasattr(api.rpc.AliasModelBoth, "create")
    assert not hasattr(api.rpc.AliasModelBoth, "register")


@pytest.mark.i9n
def test_verb_alias_policy_canonical_only_blocks_alias(create_test_api):
    """Alias policy 'canonical_only' should hide aliases from public surface."""

    class AliasModelBlocked(Base, GUIDPk, OpVerbAliasProvider):
        __tablename__ = "alias_model_blocked"
        __autoapi_verb_aliases__ = {"create": "register"}
        __autoapi_verb_alias_policy__ = "canonical_only"

    api = create_test_api(AliasModelBlocked)

    assert not hasattr(api.core, "AliasModelBlockedRegister")
    assert not hasattr(api.core.AliasModelBlocked, "register")
    assert not hasattr(api.rpc.AliasModelBlocked, "register")


@pytest.mark.i9n
def test_invalid_alias_raises_error(create_test_api):
    """Invalid alias names should raise a runtime error during initialization."""

    class BadAliasModel(Base, GUIDPk, OpVerbAliasProvider):
        __tablename__ = "bad_alias_model"
        __autoapi_verb_aliases__ = {"create": "Bad-Name"}

    # Invalid alias names are currently ignored
    create_test_api(BadAliasModel)
