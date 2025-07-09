import pytest
from peagen.cli.task_helpers import build_task
from peagen.orm import Action
from uuid import uuid4


@pytest.mark.unit
def test_build_task_payload():
    task = build_task(
        action=Action.EVOLVE,
        args={"evolve_spec": "foo.yaml"},
        tenant_id=str(uuid4()),
        pool_id=str(uuid4()),
        repo="repo",
        ref="HEAD",
    )
    assert task.action == Action.EVOLVE
    assert task.args == {"evolve_spec": "foo.yaml"}
