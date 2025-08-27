import pytest

from autoapi.v3 import alias_ctx
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types import OpVerbAliasProvider


@pytest.mark.i9n
def test_verb_alias_policy_both_routes_same_handler(create_test_api):
    """Alias decorator exposes both canonical and aliased verbs."""

    @alias_ctx(create="register")
    class AliasModelBoth(Base, GUIDPk, OpVerbAliasProvider):
        __tablename__ = "alias_model"

    api = create_test_api(AliasModelBoth)

    # Alias exposed alongside canonical verb
    assert hasattr(api.core.AliasModelBoth, "register")
    assert hasattr(api.core.AliasModelBoth, "create")
    assert hasattr(api.rpc.AliasModelBoth, "register")
    assert hasattr(api.rpc.AliasModelBoth, "create")


@pytest.mark.i9n
def test_verb_alias_policy_canonical_only_blocks_alias(create_test_api):
    """Explicit alias map hides canonical verb from public surface."""

    class AliasModelBlocked(Base, GUIDPk, OpVerbAliasProvider):
        __tablename__ = "alias_model_blocked"
        __autoapi_aliases__ = {"create": "register"}

    api = create_test_api(AliasModelBlocked)

    assert not hasattr(api.core.AliasModelBlocked, "create")
    assert hasattr(api.core.AliasModelBlocked, "register")
    assert not hasattr(api.rpc.AliasModelBlocked, "create")
    assert hasattr(api.rpc.AliasModelBlocked, "register")


@pytest.mark.i9n
def test_invalid_alias_keeps_canonical(create_test_api):
    """Invalid alias names fall back to canonical verb without raising."""

    class BadAliasModel(Base, GUIDPk, OpVerbAliasProvider):
        __tablename__ = "bad_alias_model"
        __autoapi_aliases__ = {"create": "Bad-Name"}

    api = create_test_api(BadAliasModel)

    assert hasattr(api.rpc.BadAliasModel, "create")
    assert not hasattr(api.rpc.BadAliasModel, "Bad-Name")
