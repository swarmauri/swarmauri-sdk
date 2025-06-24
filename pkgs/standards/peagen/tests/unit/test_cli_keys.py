from typer.testing import CliRunner

from peagen.cli import app
from peagen.plugins.secret_drivers import AutoGpgDriver


runner = CliRunner()


def test_show_outputs_key(tmp_path):
    AutoGpgDriver(key_dir=tmp_path)
    result = runner.invoke(app, ["keys", "show", "--key-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "BEGIN PGP PUBLIC KEY" in result.output


def test_export_openssh(tmp_path):
    AutoGpgDriver(key_dir=tmp_path)
    result = runner.invoke(
        app,
        ["keys", "export", "--key-dir", str(tmp_path), "--format", "openssh"],
    )
    assert result.exit_code == 0
    assert result.output.startswith("ssh-")


def test_add_imports_key(tmp_path):
    drv = AutoGpgDriver(key_dir=tmp_path / "src")
    dest = tmp_path / "dest"
    result = runner.invoke(
        app,
        ["keys", "add", str(drv.priv_path), "--key-dir", str(dest)],
    )
    assert result.exit_code == 0
    assert (dest / "private.asc").exists()
    assert (dest / "public.asc").exists()
