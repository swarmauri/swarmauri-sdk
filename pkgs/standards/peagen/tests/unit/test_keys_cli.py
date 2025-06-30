import json
from pathlib import Path

import pytest

from peagen.cli.commands import keys as keys_mod
from peagen.transport import KEYS_UPLOAD, KEYS_DELETE
from peagen.transport.envelope import Response
from peagen.transport.jsonrpc_schemas.keys import FetchResult


@pytest.mark.unit
def test_create_generates_key_pair(monkeypatch, tmp_path, capsys):
    captured = {}

    def fake_driver(key_dir, passphrase=None):
        captured["key_dir"] = key_dir
        captured["passphrase"] = passphrase

        class Dummy:
            pass

        return Dummy()

    monkeypatch.setattr(keys_mod, "AutoGpgDriver", fake_driver)

    keys_mod.create(passphrase="secret", key_dir=tmp_path)
    out = capsys.readouterr().out

    assert captured["key_dir"] == tmp_path
    assert captured["passphrase"] == "secret"
    assert f"Created key pair in {tmp_path}" in out


@pytest.mark.unit
def test_upload_sends_public_key(monkeypatch, tmp_path, capsys):
    (tmp_path / "public.asc").write_text("PUB")

    class DummyDriver:
        def __init__(self, key_dir):
            self.pub_path = Path(key_dir) / "public.asc"

    monkeypatch.setattr(keys_mod, "AutoGpgDriver", DummyDriver)
    captured = {}

    def fake_rpc_post(url, method, params, *, timeout, result_model=None):
        captured["url"] = url
        captured["method"] = method
        captured["params"] = params
        return Response.ok(id="1", result=None)

    monkeypatch.setattr(keys_mod, "rpc_post", fake_rpc_post)

    keys_mod.upload(ctx=None, key_dir=tmp_path, gateway_url="http://gw/rpc")
    out = capsys.readouterr().out

    assert captured["url"] == "http://gw/rpc"
    assert captured["method"] == KEYS_UPLOAD
    assert captured["params"]["public_key"] == "PUB"
    assert "Uploaded public key" in out


@pytest.mark.unit
def test_remove_posts_delete(monkeypatch, capsys):
    captured = {}

    def fake_rpc_post(url, method, params, *, timeout, result_model=None):
        captured["url"] = url
        captured["method"] = method
        captured["params"] = params
        return Response.ok(id="1", result=None)

    monkeypatch.setattr(keys_mod, "rpc_post", fake_rpc_post)

    keys_mod.remove(ctx=None, fingerprint="abc", gateway_url="http://gw")
    out = capsys.readouterr().out

    assert captured["method"] == KEYS_DELETE
    assert captured["params"]["fingerprint"] == "abc"
    assert "Removed key abc" in out


@pytest.mark.unit
def test_fetch_server_prints_response(monkeypatch, capsys):
    def fake_rpc_post(url, method, params, *, timeout, result_model=None):
        return Response.ok(id="1", result=FetchResult(keys={"k": "v"}))

    monkeypatch.setattr(keys_mod, "rpc_post", fake_rpc_post)

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
