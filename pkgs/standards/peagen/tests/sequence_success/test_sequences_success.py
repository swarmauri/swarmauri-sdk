import re
import subprocess
from pathlib import Path
import os

import yaml
import pytest
import httpx

WORKER_LIST = "Worker.list"

EXAMPLES = Path(__file__).resolve().parent / "examples"
GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway responds with a valid worker list."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
        if response.status_code != 200:
            return False
        data = response.json()
    except Exception:
        return False
    return "result" in data


def _load_command_batches(path: Path, tmpdir: Path) -> list[list[list[str]]]:
    """Return a list of command batches from ``path``."""
    data = yaml.safe_load(path.read_text()) or {}
    batches: list[list[list[str]]] = []

    def _expand(cmds: list[list[str]]) -> list[list[str]]:
        return [
            [
                part.replace("{tmpdir}", str(tmpdir)).replace("{gateway}", GATEWAY)
                for part in cmd
            ]
            for cmd in cmds
        ]

    def _handle_container(container: dict) -> None:
        if "command_sets" in container:
            for entry in container["command_sets"]:
                batch = entry.get("batch", entry)
                cmds = batch.get("commands", [])
                if cmds:
                    batches.append(_expand(cmds))
        elif "commands" in container:
            cmds = container.get("commands", [])
            if cmds:
                batches.append(_expand(cmds))

    if "batches" in data:
        for entry in data["batches"]:
            if isinstance(entry, dict):
                _handle_container(entry)
            elif isinstance(entry, list):
                batches.append(_expand(entry))
    else:
        _handle_container(data)

    return batches


@pytest.mark.sequence_success
@pytest.mark.parametrize("example", sorted(EXAMPLES.glob("*.yaml")))
def test_sequences_success(example: Path, tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")
    for batch in _load_command_batches(example, tmp_path):
        task_id: str | None = None
        for cmd in batch:
            parts = [p.replace("{task_id}", task_id or "") for p in cmd]
            result = subprocess.run(["peagen", *parts], capture_output=True, text=True)
            if result.returncode != 0:
                output = result.stdout + result.stderr
                if "Unauthorized" in output:
                    pytest.skip("gateway unauthorized")
                assert result.returncode == 0, output

            if task_id is None:
                match = re.search(r"taskId=([0-9a-f-]+)", result.stdout)
                if match:
                    task_id = match.group(1)
