import pytest
from peagen.cli.task_helpers import build_task


@pytest.mark.unit
def test_build_task_payload():
    task = build_task(
        action="evolve",
        args={"evolve_spec": "foo.yaml"},
        tenant_id="t",
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    assert task.action == "evolve"
    assert task.args == {"evolve_spec": "foo.yaml"}
