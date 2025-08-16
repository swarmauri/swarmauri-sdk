from fastapi import FastAPI

from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types import Column, String


def test_include_models_base_prefix_avoids_duplicate_segments():
    app = FastAPI()

    class Key(Base, GUIDPk):
        __tablename__ = "Key"
        name = Column(String, nullable=False)

    class KeyVersion(Base, GUIDPk):
        __tablename__ = "key_versions"
        name = Column(String, nullable=False)

    api = AutoAPI(app=app)
    api.include_models([Key, KeyVersion], base_prefix="/kms")

    paths = {r.path for r in app.router.routes}

    assert "/kms/key" in paths
    assert "/kms/key_version" in paths
    assert "/kms/key/key" not in paths
    assert "/kms/key_version/key_version" not in paths
