import pytest
from peagen.cli.commands import evolve
from peagen.cli.task_helpers import build_task


@pytest.mark.unit
def test_build_task_payload():
    task = build_task("evolve", {"evolve_spec": "foo.yaml"})
    assert task.payload["action"] == "evolve"
    assert task.payload["args"] == {"evolve_spec": "foo.yaml"}
