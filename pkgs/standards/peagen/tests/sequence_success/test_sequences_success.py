import subprocess
from pathlib import Path
import yaml
import pytest

EXAMPLES = Path(__file__).resolve().parent / "examples"


def _load_commands(path: Path, tmpdir: Path) -> list[list[str]]:
    data = yaml.safe_load(path.read_text())
    cmds = []
    for cmd in data.get("commands", []):
        cmds.append([part.replace("{tmpdir}", str(tmpdir)) for part in cmd])
    return cmds


@pytest.mark.sequence_success
@pytest.mark.parametrize("example", sorted(EXAMPLES.glob("*.yaml")))
def test_sequences_success(example: Path, tmp_path: Path) -> None:
    for cmd in _load_commands(example, tmp_path):
        result = subprocess.run(["peagen", *cmd], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
