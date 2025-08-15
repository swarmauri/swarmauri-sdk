import pytest
from autoapi.v3 import Base
from autoapi.v3.mixins import GUIDPk
from sqlalchemy import Column, String


@pytest.mark.r8n
def test_acronym_model_route(create_test_api):
    class GPGKey(Base, GUIDPk):
        __tablename__ = "gpg_keys"
        key = Column(String, nullable=False)

    api = create_test_api(GPGKey)
    paths = {route.path for route in api.router.routes}
    assert "/gpg_key" in paths
    assert all("g_p_g_key" not in p for p in paths)
