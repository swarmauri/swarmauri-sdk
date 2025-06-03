import random; random.seed(0xA11A)
from typer.testing import CliRunner
import pytest
from peagen.cli import app


@pytest.mark.unit
def test_cli_help():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
