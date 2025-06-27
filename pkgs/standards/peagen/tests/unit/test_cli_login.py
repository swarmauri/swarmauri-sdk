import httpx
from typer.testing import CliRunner
import pytest

from peagen.cli import app
import peagen.cli.commands.login as login_mod


class DummyDriver:
    def __init__(self, key_dir, passphrase):
        self.called = {"key_dir": key_dir, "passphrase": passphrase}
        self.pub_path = key_dir / "public.asc"
        self.pub_path.write_text("PUB", encoding="utf-8")


@pytest.mark.unit
def test_login_success(monkeypatch, tmp_path):
    captured = {}

    def fake_post(url, json, timeout):
        captured.update({"url": url, "json": json})

        class Resp:
            status_code = 200

        return Resp()

    monkeypatch.setattr(login_mod, "AutoGpgDriver", DummyDriver)
    monkeypatch.setattr(login_mod.httpx, "post", fake_post)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["login", "--key-dir", str(tmp_path), "--gateway-url", "http://gw/rpc"],
    )

    assert result.exit_code == 0
    assert "Logged in and uploaded public key" in result.output
    assert captured["url"] == "http://gw/rpc"
    assert captured["json"]["params"]["public_key"] == "PUB"


@pytest.mark.unit
def test_login_http_error(monkeypatch, tmp_path):
    class Resp:
        status_code = 400
        text = "fail"

    monkeypatch.setattr(login_mod, "AutoGpgDriver", DummyDriver)
    monkeypatch.setattr(login_mod.httpx, "post", lambda *a, **k: Resp())

    runner = CliRunner()
    result = runner.invoke(app, ["login", "--key-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "Failed to upload key" in result.output


@pytest.mark.unit
def test_login_request_error(monkeypatch, tmp_path):
    def fake_post(*_a, **_k):
        raise httpx.RequestError("oops")

    monkeypatch.setattr(login_mod, "AutoGpgDriver", DummyDriver)
    monkeypatch.setattr(login_mod.httpx, "post", fake_post)

    runner = CliRunner()
    result = runner.invoke(app, ["login", "--key-dir", str(tmp_path)])

    assert result.exit_code == 1
    assert "HTTP error" in result.output


@pytest.mark.unit
def test_login_passphrase(monkeypatch, tmp_path):
    captured = {}

    class CaptureDriver(DummyDriver):
        def __init__(self, key_dir, passphrase):
            super().__init__(key_dir, passphrase)
            captured.update(self.called)

    monkeypatch.setattr(login_mod, "AutoGpgDriver", CaptureDriver)
    monkeypatch.setattr(
        login_mod.httpx, "post", lambda *a, **k: type("R", (), {"status_code": 200})()
    )

    runner = CliRunner()
    result = runner.invoke(
        app, ["login", "--key-dir", str(tmp_path), "--passphrase", "s"]
    )

    assert result.exit_code == 0
    assert captured["passphrase"] == "s"
