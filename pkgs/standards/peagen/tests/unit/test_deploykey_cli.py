import json

import pytest
from typer.testing import CliRunner

from peagen.cli.commands.deploykey import local_deploykey_app, remote_deploykey_app
from peagen.core import keys_core


@pytest.mark.unit
def test_create_command_generates_new_key(monkeypatch, tmp_path):
    runner = CliRunner()

    called = {}

    def fake_create_keypair(*, key_dir, passphrase=None):
        called["key_dir"] = key_dir
        called["passphrase"] = passphrase
        return {"fingerprint": "fp", "public_key": "pub"}

    monkeypatch.setattr(keys_core, "create_keypair", fake_create_keypair)

    result = runner.invoke(
        local_deploykey_app,
        ["create", "--passphrase", "pw", "--key-dir", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert called["key_dir"] == tmp_path
    assert "Created key-pair" in result.stdout


@pytest.mark.unit
def test_list_command_enumerates_existing_keys(monkeypatch, tmp_path):
    runner = CliRunner()

    monkeypatch.setattr(
        keys_core,
        "list_local_keys",
        lambda key_dir: {"fp": "pub"} if key_dir == tmp_path else {},
        raising=False,
    )

    result = runner.invoke(local_deploykey_app, ["list", "--key-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"fp": "pub"}


@pytest.mark.unit
def test_show_command_retrieves_specific_key(monkeypatch, tmp_path):
    runner = CliRunner()

    monkeypatch.setattr(
        keys_core,
        "export_public_key",
        lambda fingerprint, key_dir, fmt: f"KEY-{fingerprint}-{fmt}",
        raising=False,
    )

    result = runner.invoke(
        local_deploykey_app,
        ["show", "fp", "--format", "ssh", "--key-dir", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == "KEY-fp-ssh"


@pytest.mark.unit
def test_upload_command_sends_key_to_remote(monkeypatch, tmp_path):
    runner = CliRunner()

    def fake_upload_public_key(*, key_dir, gateway_url, passphrase=None):
        assert key_dir == tmp_path
        assert gateway_url == "http://example.com"
        return {"fingerprint": "fp"}

    monkeypatch.setattr(keys_core, "upload_public_key", fake_upload_public_key)

    result = runner.invoke(
        remote_deploykey_app,
        ["upload", "--key-dir", str(tmp_path), "--gateway-url", "http://example.com"],
    )

    assert result.exit_code == 0
    assert "Uploaded key – fingerprint: fp" in result.stdout
