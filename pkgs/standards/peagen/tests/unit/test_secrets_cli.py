import json
import pytest
import typer
from peagen.cli.commands import secrets as secrets_cli
from peagen.transport.json_rpcschemas.worker import WORKER_LIST
from peagen.transport.json_rpcschemas.secrets import GetResult
from peagen.transport import Response


class DummyDriver:
    def __init__(self, *_, **__):
        pass

    def encrypt(self, plaintext: bytes, _recipients: list[str]):
        return b"enc:" + plaintext

    def decrypt(self, ciphertext: bytes):
        assert ciphertext.startswith(b"enc:")
        return ciphertext[4:]


@pytest.fixture(autouse=True)
def patch_driver(monkeypatch):
    """Use deterministic encryption for tests."""
    monkeypatch.setattr(secrets_cli, "AutoGpgDriver", DummyDriver)


class Ctx:
    obj = {"gateway_url": "http://gw"}


def test_pool_worker_pubs_collects_keys(monkeypatch):
    captured = {}

    def fake_rpc_post(url, method, params, *, timeout, result_model=None):
        captured["url"] = url
        captured["method"] = method
        captured["params"] = params
        res = [
            {"advertises": {"public_key": "A"}},
            {"advertises": {"pubkey": "B"}},
        ]
        return Response.ok(id="1", result=res)

    monkeypatch.setattr(secrets_cli, "rpc_post", fake_rpc_post)
    keys = secrets_cli._pool_worker_pubs("p", "http://gw")
    assert keys == ["A", "B"]
    assert captured["method"] == WORKER_LIST


def test_pool_worker_pubs_handles_error(monkeypatch):
    def fake_rpc_post(*_, **__):
        raise RuntimeError

    monkeypatch.setattr(secrets_cli, "rpc_post", fake_rpc_post)
    keys = secrets_cli._pool_worker_pubs("p", "http://gw")
    assert keys == []


def test_local_add_stores_secret(monkeypatch, tmp_path):
    store = tmp_path / "store.json"
    monkeypatch.setattr(secrets_cli, "STORE_FILE", store)
    secrets_cli.add("NAME", "value", recipients=[])
    data = json.loads(store.read_text())
    assert "NAME" in data
    assert data["NAME"].startswith("enc:")


def test_local_get_outputs_secret(monkeypatch, tmp_path):
    store = tmp_path / "store.json"
    store.write_text(json.dumps({"NAME": "enc:value"}))
    monkeypatch.setattr(secrets_cli, "STORE_FILE", store)
    out = []
    monkeypatch.setattr(typer, "echo", lambda msg: out.append(msg))
    secrets_cli.get("NAME")
    assert out == ["value"]


def test_local_get_unknown(monkeypatch, tmp_path):
    store = tmp_path / "store.json"
    store.write_text("{}")
    monkeypatch.setattr(secrets_cli, "STORE_FILE", store)
    with pytest.raises(typer.BadParameter):
        secrets_cli.get("NAME")


def test_local_remove(monkeypatch, tmp_path):
    store = tmp_path / "store.json"
    store.write_text(json.dumps({"NAME": "enc:value"}))
    monkeypatch.setattr(secrets_cli, "STORE_FILE", store)
    secrets_cli.remove("NAME")
    assert json.loads(store.read_text()) == {}


def test_remote_add_posts(monkeypatch):
    posted = {}

    def fake_rpc_post(url, method, params, *, timeout, result_model=None):
        posted["method"] = method
        posted["params"] = params
        return Response.ok(id="1", result=None)

    monkeypatch.setattr(secrets_cli, "rpc_post", fake_rpc_post)
    monkeypatch.setattr(secrets_cli, "_pool_worker_pubs", lambda pool, url: ["P"])

    ctx = Ctx()
    secrets_cli.remote_add(
        ctx,
        "ID",
        "v",
        version=1,
        recipient=[],
        pool="p",
    )
    assert posted["params"]["cipher"].startswith("enc:")
    assert posted["params"]["name"] == "ID"
    assert posted["params"]["version"] == 1


def test_remote_get(monkeypatch):
    posted = {}

    def fake_rpc_post(url, method, params, *, timeout, result_model=None):
        posted["method"] = method
        posted["params"] = params
        return Response.ok(id="1", result=GetResult(secret="enc:value"))

    monkeypatch.setattr(secrets_cli, "rpc_post", fake_rpc_post)
    out = []
    monkeypatch.setattr(typer, "echo", lambda msg: out.append(msg))
    ctx = Ctx()
    secrets_cli.remote_get(
        ctx,
        "ID",
        gateway_url="https://gw.peagen.com",
        pool="default",
    )
    assert out == ["value"]
    assert posted["method"] == "Secrets.get"
    assert posted["params"] == {"name": "ID", "tenant_id": "default"}


def test_remote_remove(monkeypatch):
    posted = {}

    def fake_rpc_post(url, method, params, *, timeout, result_model=None):
        posted["method"] = method
        posted["params"] = params
        return Response.ok(id="1", result=None)

    monkeypatch.setattr(secrets_cli, "rpc_post", fake_rpc_post)
    ctx = Ctx()
    secrets_cli.remote_remove(
        ctx,
        "ID",
        version=2,
        gateway_url="https://gw.peagen.com",
        pool="default",
    )
    assert posted["method"] == "Secrets.delete"
    assert posted["params"] == {"name": "ID", "version": 2, "tenant_id": "default"}
