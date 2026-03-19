from tigrbl_base._base._alias_base import AliasBase
from tigrbl_core._spec.alias_spec import AliasSpec


def test_alias_base_inheritance_and_properties() -> None:
    alias = AliasBase(
        _alias="create_user",
        _request_schema="Req",
        _response_schema="Res",
        _persist="always",
        _arity="one",
        _rest=True,
    )

    assert isinstance(alias, AliasSpec)
    assert alias.alias == "create_user"
    assert alias.request_schema == "Req"
    assert alias.response_schema == "Res"
    assert alias.persist == "always"
    assert alias.arity == "one"
    assert alias.rest is True
