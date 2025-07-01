import json
from pathlib import Path

import pytest

from peagen.cli.commands import keys as keys_mod


@pytest.mark.unit
def test_create_generates_key_pair(monkeypatch, tmp_path, capsys):
    captured = {}

    def fake_create(key_dir, passphrase=None):
        captured["key_dir"] = key_dir
        captured["passphrase"] = passphrase
        return {}

    monkeypatch.setattr(keys_mod.keys_core, "create_keypair", fake_create)

    keys_mod.create(passphrase="secret", key_dir=tmp_path)
    out = capsys.readouterr().out

    assert captured["key_dir"] == tmp_path
    assert captured["passphrase"] == "secret"
    assert f"Created key pair in {tmp_path}" in out


@pytest.mark.unit
def test_upload_sends_public_key(monkeypatch, tmp_path, capsys):
    captured = {}

    def fake_upload(*, key_dir, gateway_url):
        captured["key_dir"] = key_dir
        captured["gateway_url"] = gateway_url
        return {"fingerprint": "FP"}

    monkeypatch.setattr(keys_mod.keys_core, "upload_public_key", fake_upload)

    keys_mod.upload(ctx=None, key_dir=tmp_path, gateway_url="http://gw/rpc")
    out = capsys.readouterr().out

    assert captured["gateway_url"] == "http://gw/rpc"
    assert captured["key_dir"] == tmp_path
    assert "Uploaded public key" in out


@pytest.mark.unit
def test_remove_posts_delete(monkeypatch, capsys):
    captured = {}

    def fake_remove(*, fingerprint, gateway_url):
        captured["fingerprint"] = fingerprint
        captured["gateway_url"] = gateway_url
        return {"ok": True}

    monkeypatch.setattr(keys_mod.keys_core, "remove_public_key", fake_remove)

    keys_mod.remove(ctx=None, fingerprint="abc", gateway_url="http://gw")
    out = capsys.readouterr().out

    assert captured["fingerprint"] == "abc"
    assert captured["gateway_url"] == "http://gw"
    assert "Removed key abc" in out


@pytest.mark.unit
def test_fetch_server_prints_response(monkeypatch, capsys):
    def fake_fetch(*, gateway_url):
        return {"keys": {"k": "v"}}

    monkeypatch.setattr(keys_mod.keys_core, "fetch_server_keys", fake_fetch)

    keys_mod.fetch_server(ctx=None, gateway_url="http://gw")
    out = capsys.readouterr().out

    assert json.loads(out) == {"keys": {"k": "v"}}


@pytest.mark.unit
def test_list_keys(monkeypatch, capsys):
    monkeypatch.setattr(keys_mod.keys_core, "list_local_keys", lambda p: {"f": "p"})
    keys_mod.list_keys(key_dir=Path("x"))
    out = capsys.readouterr().out
    assert json.loads(out) == {"f": "p"}


@pytest.mark.unit
def test_show_key(monkeypatch, capsys):
    def fake_export(fpr, *, key_dir, fmt):
        assert key_dir == Path("x")
        assert fmt == "openssh"
        return "ssh"

    monkeypatch.setattr(keys_mod.keys_core, "export_public_key", fake_export)
    keys_mod.show("abc", fmt="openssh", key_dir=Path("x"))
    out = capsys.readouterr().out
    assert out.strip() == "ssh"


@pytest.mark.unit
def test_add_key(monkeypatch, capsys):
    monkeypatch.setattr(
        keys_mod.keys_core, "add_key", lambda *a, **k: {"fingerprint": "f", "path": "p"}
    )
    keys_mod.add(Path("pub"), key_dir=Path("x"), name="n")
    out = capsys.readouterr().out
    assert json.loads(out) == {"fingerprint": "f", "path": "p"}
