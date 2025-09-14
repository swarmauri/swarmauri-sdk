import pytest
from peagen.cli.task_helpers import build_task
from peagen.orm import Action


@pytest.mark.unit
def test_build_task_payload():
    task = build_task(
        action="evolve",
        args={"evolve_spec": "foo.yaml"},
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    assert task.action == Action.EVOLVE
    assert task.args == {"evolve_spec": "foo.yaml"}
