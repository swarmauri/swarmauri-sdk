import pytest
from typer.testing import CliRunner
from peagen.commands.process import process_app
from unittest.mock import patch, MagicMock


@pytest.mark.r8n
def test_process_cli_allows_no_provider(tmp_path):
    payload = tmp_path / "proj.yaml"
    payload.write_text("schemaVersion: '1.0'\nPROJECTS: []", encoding="utf-8")
    runner = CliRunner()
    dummy_registry = {
        "storage_adapters": {
            "file": type("Dummy", (), {"__init__": lambda *a, **k: None})
        }
    }
    with (
        patch("peagen.commands.process.install_template_sets", return_value=[]),
        patch("peagen.commands.process.materialise_packages", return_value=[]),
        patch("peagen.commands.process.registry", dummy_registry),
        patch("peagen.commands.process.Peagen") as MockPeagen,
    ):
        MockPeagen.return_value.process_all_projects.return_value = []
        with patch(
            "peagen.commands.process.load_peagen_toml",
            return_value={"source_packages": [], "template_sets": []},
        ):
            result = runner.invoke(process_app, [str(payload)])
        assert result.exit_code == 0
        MockPeagen.return_value.process_all_projects.assert_called_once()


@pytest.mark.r8n
def test_process_cli_start_idx_and_file_error(tmp_path):
    payload = tmp_path / "proj.yaml"
    payload.write_text("schemaVersion: '1.0'\nPROJECTS: []", encoding="utf-8")
    runner = CliRunner()
    dummy_registry = {
        "storage_adapters": {
            "file": type("Dummy", (), {"__init__": lambda *a, **k: None})
        }
    }
    with (
        patch("peagen.commands.process.install_template_sets", return_value=[]),
        patch("peagen.commands.process.materialise_packages", return_value=[]),
        patch("peagen.commands.process.registry", dummy_registry),
        patch("peagen.commands.process.Peagen"),
    ):
        with patch(
            "peagen.commands.process.load_peagen_toml",
            return_value={"source_packages": [], "template_sets": []},
        ):
            result = runner.invoke(
                process_app,
                [str(payload), "--start-idx", "1", "--start-file", "foo"],
            )
        assert result.exit_code != 0
        assert "Invalid combination of flags" in result.output
