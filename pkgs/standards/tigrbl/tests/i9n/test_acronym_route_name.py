import pytest
from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.i9n
def test_acronym_model_route(create_test_api):
    class GPGKey(Base, GUIDPk):
        __tablename__ = "gpg_keys"
        key = Column(String, nullable=False)

    api = create_test_api(GPGKey)
    paths = {route.path for route in api.router.routes}
    assert "/gpgkey" in paths
    assert all("g_p_g_key" not in p for p in paths)
