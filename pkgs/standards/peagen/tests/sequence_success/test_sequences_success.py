import re
import subprocess
from pathlib import Path

import yaml
import pytest

EXAMPLES = Path(__file__).resolve().parent / "examples"


def _load_command_batches(path: Path, tmpdir: Path) -> list[list[list[str]]]:
    """Return a list of command batches from ``path``."""
    data = yaml.safe_load(path.read_text()) or {}
    batches: list[list[list[str]]] = []

    if "command_sets" in data:
        for entry in data["command_sets"]:
            batch = entry.get("batch", entry)
            cmds = [
                [part.replace("{tmpdir}", str(tmpdir)) for part in cmd]
                for cmd in batch.get("commands", [])
            ]
            if cmds:
                batches.append(cmds)

    elif "batches" in data:
        for batch in data["batches"]:
            cmds = [
                [part.replace("{tmpdir}", str(tmpdir)) for part in cmd] for cmd in batch
            ]
            if cmds:
                batches.append(cmds)

    elif "commands" in data:
        cmds = [
            [part.replace("{tmpdir}", str(tmpdir)) for part in cmd]
            for cmd in data["commands"]
        ]
        if cmds:
            batches.append(cmds)

    return batches


@pytest.mark.sequence_success
@pytest.mark.parametrize("example", sorted(EXAMPLES.glob("*.yaml")))
def test_sequences_success(example: Path, tmp_path: Path) -> None:
    for batch in _load_command_batches(example, tmp_path):
        task_id: str | None = None
        for cmd in batch:
            parts = [p.replace("{task_id}", task_id or "") for p in cmd]
            result = subprocess.run(["peagen", *parts], capture_output=True, text=True)
            assert result.returncode == 0, result.stdout + result.stderr

            if task_id is None:
                match = re.search(r"taskId=([0-9a-f-]+)", result.stdout)
                if match:
                    task_id = match.group(1)
