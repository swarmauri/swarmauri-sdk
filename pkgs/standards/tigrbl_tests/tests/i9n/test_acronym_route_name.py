import pytest
from tigrbl import TableBase
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.i9n
def test_acronym_model_route_name_uses_compact_lowercase_resource() -> None:
    class GPGKey(TableBase, GUIDPk):
        __tablename__ = "gpg_keys"
        key = Column(String, nullable=False)

    assert GPGKey.resource_name == "gpgkey"
    assert "g_p_g_key" not in GPGKey.resource_name


@pytest.mark.i9n
def test_resource_name_uses_explicit_resource_override() -> None:
    class GPGKey(TableBase, GUIDPk):
        __tablename__ = "gpg_keys"
        __resource__ = "gpg-key"
        key = Column(String, nullable=False)

    assert GPGKey.resource_name == "gpg-key"
