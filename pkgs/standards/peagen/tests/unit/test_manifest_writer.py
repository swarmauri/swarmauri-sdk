import json
import threading
from pathlib import Path

import pytest

from peagen.manifest_writer import ManifestWriter


class DummyAdapter:
    def __init__(self):
        self.uploaded = []
        self.root_uri = "s3://unit/"

    def upload(self, key: str, fh):
        # record only the key
        self.uploaded.append(key)


@pytest.mark.unit
def test_manifest_writer_add_and_finalise(tmp_path: Path, monkeypatch):
    adapter = DummyAdapter()

    class FakeThread:
        def __init__(self, target, name=None, daemon=None):
            self.target = target

        def start(self):
            self.target()

    monkeypatch.setattr(threading, "Thread", FakeThread)

    writer = ManifestWriter(slug="proj", adapter=adapter, tmp_root=tmp_path)
    writer.add({"file": "a.txt"})
    writer.add({"file": "b.txt"})

    uri = writer.finalise()

    assert uri == "s3://unit/.peagen/proj_manifest.json"
    manifest_path = tmp_path / "proj_manifest.json"
    data = json.loads(manifest_path.read_text())
    assert data["generated"] == ["a.txt", "b.txt"]
    assert not (tmp_path / "proj_manifest.partial.jsonl").exists()

    assert f".peagen/{writer.path.name}" in adapter.uploaded
    assert ".peagen/proj_manifest.json" in adapter.uploaded
