import json
from pathlib import Path

import pytest

from peagen.cli.commands import keys as keys_mod


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

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json

        class Resp:
            pass

        return Resp()

    monkeypatch.setattr(keys_mod, "httpx", type("X", (), {"post": fake_post}))

    keys_mod.upload(ctx=None, key_dir=tmp_path, gateway_url="http://gw/rpc")
    out = capsys.readouterr().out

    assert captured["url"] == "http://gw/rpc"
    assert captured["json"]["method"] == "Keys.upload"
    assert captured["json"]["params"]["public_key"] == "PUB"
    assert "Uploaded public key" in out


@pytest.mark.unit
def test_remove_posts_delete(monkeypatch, capsys):
    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json

        class Resp:
            pass

        return Resp()

    monkeypatch.setattr(keys_mod, "httpx", type("X", (), {"post": fake_post}))

    keys_mod.remove(ctx=None, fingerprint="abc", gateway_url="http://gw")
    out = capsys.readouterr().out

    assert captured["json"]["method"] == "Keys.delete"
    assert captured["json"]["params"]["fingerprint"] == "abc"
    assert "Removed key abc" in out


@pytest.mark.unit
def test_fetch_server_prints_response(monkeypatch, capsys):
    def fake_post(url, json, timeout):
        class Resp:
            def json(self):
                return {"result": {"k": "v"}}

        return Resp()

    monkeypatch.setattr(keys_mod, "httpx", type("X", (), {"post": fake_post}))

    keys_mod.fetch_server(ctx=None, gateway_url="http://gw")
    out = capsys.readouterr().out

    assert json.loads(out) == {"k": "v"}
