import pytest
from peagen.cli.commands import evolve


@pytest.mark.unit
def test_build_task_payload():
    task = evolve._build_task({"evolve_spec": "foo.yaml"})
    assert task.payload["action"] == "evolve"
    assert task.payload["args"] == {"evolve_spec": "foo.yaml"}
