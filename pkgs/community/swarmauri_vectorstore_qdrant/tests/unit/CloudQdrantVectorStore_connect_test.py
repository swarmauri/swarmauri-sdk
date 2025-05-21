import importlib
import sys
import types

import pytest


def _patch_qdrant(monkeypatch, existing=None):
    existing = existing or []
    dummy_module = types.ModuleType("qdrant_client")

    class DummyCollection:
        def __init__(self, name):
            self.name = name

    class DummyClient:
        def __init__(self, api_key=None, url=None):
            self.api_key = api_key
            self.url = url
            self.recreated = False

        def get_collections(self):
            cols = [DummyCollection(name) for name in existing]
            return types.SimpleNamespace(collections=cols)

        def recreate_collection(self, collection_name, vectors_config):
            self.recreated = True

    models = types.SimpleNamespace(
        VectorParams=object,
        Distance=types.SimpleNamespace(COSINE="cosine"),
        PointStruct=object,
    )

    dummy_module.QdrantClient = DummyClient
    dummy_module.models = models
    monkeypatch.setitem(sys.modules, "qdrant_client", dummy_module)
    monkeypatch.setitem(sys.modules, "qdrant_client.models", models)
    importlib.invalidate_caches()
    module = importlib.import_module(
        "swarmauri_vectorstore_qdrant.CloudQdrantVectorStore"
    )
    importlib.reload(module)
    return module.CloudQdrantVectorStore, DummyClient


@pytest.mark.unit
def test_connect_creates_collection(monkeypatch):
    CloudQdrantVectorStore, DummyClient = _patch_qdrant(monkeypatch)
    vs = CloudQdrantVectorStore(
        api_key="k",
        collection_name="foo",
        vector_size=10,
        url="http://localhost",
    )
    vs.connect()
    assert isinstance(vs.client, DummyClient)
    assert vs.client.recreated


@pytest.mark.unit
def test_connect_skips_existing(monkeypatch):
    CloudQdrantVectorStore, DummyClient = _patch_qdrant(monkeypatch, existing=["bar"])
    vs = CloudQdrantVectorStore(
        api_key="k",
        collection_name="bar",
        vector_size=10,
        url="http://localhost",
    )
    vs.connect()
    assert isinstance(vs.client, DummyClient)
    assert not vs.client.recreated
