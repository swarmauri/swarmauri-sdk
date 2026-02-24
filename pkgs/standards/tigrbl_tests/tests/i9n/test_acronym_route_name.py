import pytest
from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


@pytest.mark.i9n
def test_acronym_model_route(create_test_router):
    class GPGKey(Base, GUIDPk):
        __tablename__ = "gpg_keys"
        key = Column(String, nullable=False)

<<<<<<< HEAD
    router = create_test_router(GPGKey)
    paths = {route.path for route in router.routes}
=======
    router = create_test_api(GPGKey)
    paths = {route.path for route in router.router.routes}
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    assert "/gpgkey" in paths
    assert all("g_p_g_key" not in p for p in paths)
