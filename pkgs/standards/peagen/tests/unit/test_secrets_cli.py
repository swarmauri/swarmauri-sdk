import json
from pathlib import Path

import pytest
import typer
from peagen.cli.commands import secrets as secrets_cli
from peagen.core import secrets_core
from peagen.transport.client import RPCTransportError
from peagen.transport.jsonrpc_schemas.worker import WORKER_LIST


import tempfile


class DummyDriver:
    def __init__(self, *_, **__):
        self.key_dir = Path(tempfile.mkdtemp())
        self.pub_path = self.key_dir / "public.asc"
        self.priv_path = self.key_dir / "private.asc"
        self.pub_path.write_text("PUB")
        self.priv_path.write_text("PRIV")

    def encrypt(self, plaintext: bytes, _recipients: list[str]):
        return b"enc:" + plaintext

    def decrypt(self, ciphertext: bytes):
        assert ciphertext.startswith(b"enc:")
        return ciphertext[4:]


@pytest.fixture(autouse=True)
def patch_driver(monkeypatch):
    """Use deterministic encryption for tests."""
    monkeypatch.setattr(secrets_core, "AutoGpgDriver", DummyDriver)


class Ctx:
    obj = {"gateway_url": "http://gw"}


def test_pool_worker_pubs_collects_keys(monkeypatch):
    captured = {}

    def fake_rpc(url, method, params, *, expect, sign=False):
        captured["url"] = url
        captured["method"] = method

        class DummyRes:
            root = [
                {"advertises": {"public_key": "A"}},
                {"advertises": {"pubkey": "B"}},
            ]

        return DummyRes()

    monkeypatch.setattr(secrets_core, "send_jsonrpc_request", fake_rpc)
    keys = secrets_core._pool_worker_pubs("p", "http://gw")
    assert keys == ["A", "B"]
    assert captured["method"] == WORKER_LIST


def test_pool_worker_pubs_handles_error(monkeypatch):
    def fake_rpc(*_a, **_k):
        raise RPCTransportError("fail")

    monkeypatch.setattr(secrets_core, "send_jsonrpc_request", fake_rpc)
    keys = secrets_core._pool_worker_pubs("p", "http://gw")
    assert keys == []


def test_local_add_stores_secret(monkeypatch, tmp_path):
    store = tmp_path / "store.json"
    monkeypatch.setattr(secrets_core, "STORE_FILE", store)
    secrets_cli.add_local_secret("NAME", "value", recipients=[])
    data = json.loads(store.read_text())
    assert "NAME" in data
    assert data["NAME"].startswith("enc:")


def test_local_get_outputs_secret(monkeypatch, tmp_path):
    store = tmp_path / "store.json"
    store.write_text(json.dumps({"NAME": "enc:value"}))
    monkeypatch.setattr(secrets_core, "STORE_FILE", store)
    out = []
    monkeypatch.setattr(typer, "echo", lambda msg: out.append(msg))
    secrets_cli.get_local_secret("NAME")
    assert out == ["value"]


def test_local_get_unknown(monkeypatch, tmp_path):
    store = tmp_path / "store.json"
    store.write_text("{}")
    monkeypatch.setattr(secrets_core, "STORE_FILE", store)
    with pytest.raises(typer.Exit):
        secrets_cli.get_local_secret("NAME")


def test_local_remove(monkeypatch, tmp_path):
    store = tmp_path / "store.json"
    store.write_text(json.dumps({"NAME": "enc:value"}))
    monkeypatch.setattr(secrets_core, "STORE_FILE", store)
    secrets_cli.remove_local_secret("NAME")
    assert json.loads(store.read_text()) == {}


def test_remote_add_posts(monkeypatch):
    captured = {}

    def fake_add(secret_id, value, *, gateway_url, version, recipients, pool):
        captured.update(
            {
                "secret_id": secret_id,
                "value": value,
                "gateway_url": gateway_url,
                "version": version,
                "recipients": recipients,
                "pool": pool,
            }
        )
        return {}

    monkeypatch.setattr(secrets_core, "add_remote_secret", fake_add)

    ctx = Ctx()
    secrets_cli.add_remote_secret(
        ctx,
        "ID",
        "v",
        version=1,
        recipient=[],
        pool="p",
    )
    assert captured["secret_id"] == "ID"
    assert captured["gateway_url"] == "http://gw"


def test_remote_get(monkeypatch):
    captured = {}

    def fake_get(secret_id, *, gateway_url):
        captured.update({"secret_id": secret_id, "gateway_url": gateway_url})
        return "value"

    monkeypatch.setattr(secrets_core, "get_remote_secret", fake_get)
    out = []
    monkeypatch.setattr(typer, "echo", lambda msg: out.append(msg))
    ctx = Ctx()
    secrets_cli.get_remote_secret(
        ctx,
        "ID",
        gateway_url="https://gw.peagen.com",
    )
    assert out == ["value"]
    assert captured["secret_id"] == "ID"


def test_remote_remove(monkeypatch):
    captured = {}

    def fake_remove(secret_id, *, gateway_url, version=None):
        captured.update(
            {"secret_id": secret_id, "gateway_url": gateway_url, "version": version}
        )
        return {"ok": True}

    monkeypatch.setattr(secrets_core, "remove_remote_secret", fake_remove)
    ctx = Ctx()
    secrets_cli.remove_remote_secret(
        ctx,
        "ID",
        version=2,
        gateway_url="https://gw.peagen.com",
    )
    assert captured["secret_id"] == "ID"
    assert captured["gateway_url"] == "http://gw"
