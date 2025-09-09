"""Verify IO verb exposure for user and tenant columns."""

from tigrbl_auth.orm.user import User
from tigrbl_auth.orm.tenant import Tenant


def test_user_column_io() -> None:
    specs = User.__autoapi_colspecs__
    expected_in = {"create", "update", "replace"}
    assert set(specs["username"].io.in_verbs) == expected_in
    assert set(specs["email"].io.in_verbs) == expected_in
    assert set(specs["password_hash"].io.in_verbs) == expected_in
    assert set(specs["username"].io.out_verbs) >= {"read", "list"}
    assert set(specs["email"].io.out_verbs) >= {"read", "list"}


def test_tenant_column_io() -> None:
    specs = Tenant.__autoapi_colspecs__
    expected_in = {"create", "update", "replace"}
    for col in ("name", "email"):
        assert set(specs[col].io.in_verbs) == expected_in
        assert set(specs[col].io.out_verbs) >= {"read", "list"}
