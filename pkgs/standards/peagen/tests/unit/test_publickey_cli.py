from pathlib import Path

import pytest
from typer.testing import CliRunner

from peagen.cli.commands.publickey import (
    local_publickey_app,
    remote_publickey_app,
)


@pytest.mark.unit
def test_create_command_generates_key_pair(tmp_path: Path) -> None:
    runner = CliRunner()
    key_dir = tmp_path / "keys"

    result = runner.invoke(
        local_publickey_app,
        ["--key-dir", str(key_dir), "--passphrase", "secret"],
    )

    assert result.exit_code == 0
    assert (key_dir / "ssh-public").exists()
    assert (key_dir / "ssh-private").exists()
    assert f"Created key-pair in {key_dir}" in result.stdout


@pytest.mark.unit
def test_upload_command_sends_public_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runner = CliRunner()
    key_dir = tmp_path / "keys"

    runner.invoke(
        local_publickey_app,
        ["--key-dir", str(key_dir), "--passphrase", "secret"],
    )

    called: dict[str, object] = {}

    def fake_login(*, key_dir: Path, passphrase: str, gateway_url: str):
        called["key_dir"] = key_dir
        called["passphrase"] = passphrase
        called["gateway_url"] = gateway_url
        return {"result": "ok"}

    monkeypatch.setattr(
        "peagen.cli.commands.publickey.core_login",
        fake_login,
    )

    result = runner.invoke(
        remote_publickey_app,
        [
            "--key-dir",
            str(key_dir),
            "--passphrase",
            "secret",
            "--gateway-url",
            "https://example.com",
        ],
    )

    assert result.exit_code == 0
    assert "Uploaded public key" in result.stdout
    assert called == {
        "key_dir": key_dir,
        "passphrase": "secret",
        "gateway_url": "https://example.com/rpc",
    }
