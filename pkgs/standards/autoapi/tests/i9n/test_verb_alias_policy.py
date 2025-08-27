"""Tests for AutoAPI verb aliasing and policy handling."""

import pytest

from autoapi.v3 import Base
from autoapi.v3.mixins import GUIDPk


@pytest.mark.i9n
def test_verb_alias_policy_both_routes_same_handler(create_test_api):
    """Canonical verbs and aliases should map to the same handler when allowed."""

    class AliasModelBoth(Base, GUIDPk):
        __tablename__ = "alias_model"
        __autoapi_verb_aliases__ = {"create": "register"}
        __autoapi_verb_alias_policy__ = "both"

    api = create_test_api(AliasModelBoth)

    # Alias exposed alongside canonical verb
    assert hasattr(api.core.AliasModelBoth, "register")
    assert api.core.AliasModelBoth.register is api.core.AliasModelBoth.create
    assert api.core.AliasModelBothRegister is api.core.AliasModelBothCreate

    m_id_create = f"{AliasModelBoth.__name__}.create"
    m_id_register = f"{AliasModelBoth.__name__}.register"
    assert api.rpc[m_id_create] is api.rpc[m_id_register]


@pytest.mark.i9n
def test_verb_alias_policy_canonical_only_blocks_alias(create_test_api):
    """Alias policy 'canonical_only' should hide aliases from public surface."""

    class AliasModelBlocked(Base, GUIDPk):
        __tablename__ = "alias_model_blocked"
        __autoapi_verb_aliases__ = {"create": "register"}
        __autoapi_verb_alias_policy__ = "canonical_only"

    api = create_test_api(AliasModelBlocked)

    assert not hasattr(api.core, "AliasModelBlockedRegister")
    assert not hasattr(api.core.AliasModelBlocked, "register")
    m_id_register = f"{AliasModelBlocked.__name__}.register"
    with pytest.raises(KeyError):
        api.rpc[m_id_register]


@pytest.mark.i9n
def test_invalid_alias_raises_error(create_test_api):
    """Invalid alias names should raise a runtime error during initialization."""

    class BadAliasModel(Base, GUIDPk):
        __tablename__ = "bad_alias_model"
        __autoapi_verb_aliases__ = {"create": "Bad-Name"}

    with pytest.raises(RuntimeError):
        create_test_api(BadAliasModel)
