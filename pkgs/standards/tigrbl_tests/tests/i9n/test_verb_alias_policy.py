"""Tests for Tigrbl verb alias configuration (currently ignored)."""

import pytest
from tigrbl import TableBase
from tigrbl.orm.mixins import GUIDPk


@pytest.mark.i9n
def test_verb_alias_policy_both_routes_same_handler(create_test_app) -> None:
    """Verb aliases are ignored; only canonical verbs are exposed."""

    class AliasModelBoth(TableBase, GUIDPk):
        __tablename__ = "alias_model"
        __tigrbl_verb_aliases__ = {"create": "register"}
        __tigrbl_verb_alias_policy__ = "both"

    app = create_test_app(AliasModelBoth)

    # Only the canonical verb is available.
    assert hasattr(app.core.AliasModelBoth, "create")
    assert not hasattr(app.core.AliasModelBoth, "register")
    assert hasattr(app.rpc.AliasModelBoth, "create")
    assert not hasattr(app.rpc.AliasModelBoth, "register")


@pytest.mark.i9n
def test_verb_alias_policy_canonical_only_blocks_alias(create_test_app) -> None:
    """Alias policy has no effect; aliases remain hidden."""

    class AliasModelBlocked(TableBase, GUIDPk):
        __tablename__ = "alias_model_blocked"
        __tigrbl_verb_aliases__ = {"create": "register"}
        __tigrbl_verb_alias_policy__ = "canonical_only"

    app = create_test_app(AliasModelBlocked)

    assert hasattr(app.core.AliasModelBlocked, "create")
    assert not hasattr(app.core.AliasModelBlocked, "register")
    assert hasattr(app.rpc.AliasModelBlocked, "create")
    assert not hasattr(app.rpc.AliasModelBlocked, "register")


@pytest.mark.i9n
def test_invalid_alias_is_ignored(create_test_app) -> None:
    """Invalid alias names are ignored without raising errors."""

    class BadAliasModel(TableBase, GUIDPk):
        __tablename__ = "bad_alias_model"
        __tigrbl_verb_aliases__ = {"create": "Bad-Name"}

    app = create_test_app(BadAliasModel)

    assert hasattr(app.core.BadAliasModel, "create")
    assert not hasattr(app.core.BadAliasModel, "Bad-Name")
    assert hasattr(app.rpc.BadAliasModel, "create")
    assert not hasattr(app.rpc.BadAliasModel, "Bad-Name")
