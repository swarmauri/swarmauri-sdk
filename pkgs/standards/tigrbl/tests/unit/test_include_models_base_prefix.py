from tigrbl.types import App

from tigrbl import TigrblApp
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_include_models_base_prefix_avoids_duplicate_segments():
    app = App()

    class Key(Base, GUIDPk):
        __tablename__ = "Key"
        name = Column(String, nullable=False)

    class KeyVersion(Base, GUIDPk):
        __tablename__ = "key_versions"
        name = Column(String, nullable=False)

    api = TigrblApp()
    api.include_models([Key, KeyVersion], base_prefix="/kms")
    app.include_router(api.router)

    paths = {r.path for r in app.router.routes}

    assert "/kms/key" in paths
    assert "/kms/keyversion" in paths
    assert "/kms/key/key" not in paths
    assert "/kms/keyversion/keyversion" not in paths
