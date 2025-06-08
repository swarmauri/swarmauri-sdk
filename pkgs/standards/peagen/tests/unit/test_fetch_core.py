import json
from pathlib import Path
import pytest

import peagen.core.fetch_core as fetch_core


@pytest.mark.unit
def test_download_manifest_reads_file(tmp_path: Path):
    manifest = {"workspace_uri": "file:///ws"}
    f = tmp_path / "m.json"
    f.write_text(json.dumps(manifest))

    out = fetch_core._download_manifest(str(f))
    assert out == manifest


@pytest.mark.unit
def test_fetch_single_uses_storage_adapter(tmp_path: Path, monkeypatch):
    manifest = {
        "workspace_uri": "file:///ws",
        "template_sets": ["set"],
        "source_packages": ["pkg"],
    }
    man_file = tmp_path / "manifest.json"
    man_file.write_text(json.dumps(manifest))

    calls = {}

    class DummyAdapter:
        def __init__(self, uri: str):
            calls["uri"] = uri

        def download_prefix(self, prefix: str, dest: Path):
            calls["download"] = dest

    monkeypatch.setattr(fetch_core, "make_adapter_for_uri", lambda uri: DummyAdapter(uri))
    monkeypatch.setattr(fetch_core, "install_template_sets", lambda sets: calls.setdefault("install", sets))
    monkeypatch.setattr(fetch_core, "materialise_packages", lambda pkgs, workspace, upload=False: calls.setdefault("packages", pkgs))

    res = fetch_core.fetch_single(str(man_file), dest_root=tmp_path)
    assert res["manifest"] == str(man_file)
    assert calls["uri"] == "file:///ws"
    assert calls["download"] == tmp_path
    assert calls["install"] == ["set"]
    assert calls["packages"] == ["pkg"]
