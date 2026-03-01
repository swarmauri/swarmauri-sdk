from tigrbl import TigrblApp, TigrblRouter

from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_inclued_tables_base_prefix_avoids_duplicate_segments():
    app = TigrblApp()

    class Key(Base, GUIDPk):
        __tablename__ = "Key"
        name = Column(String, nullable=False)

    class KeyVersion(Base, GUIDPk):
        __tablename__ = "key_versions"
        name = Column(String, nullable=False)

    router = TigrblRouter()
    app.include_tables([Key, KeyVersion], base_prefix="/kms")
    app.include_router(router)

    paths = {r.path for r in app.router.routes}

    assert "/kms/key" in paths
    assert "/kms/keyversion" in paths
    assert "/kms/key/key" not in paths
    assert "/kms/keyversion/keyversion" not in paths
