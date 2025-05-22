import pytest
from typer.testing import CliRunner

from peagen.cli import app


@pytest.mark.i9n
def test_template_set_list_contains_known_set():
    """Run ``peagen template-set list`` and check a known template-set exists."""
    runner = CliRunner()
    result = runner.invoke(app, ["template-set", "list"])
    assert result.exit_code == 0, result.output
    assert "swarmauri_base" in result.output
