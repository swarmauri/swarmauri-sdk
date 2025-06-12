import json
from pathlib import Path

import pytest
import yaml

from peagen.core import TaskChainer, chain_hash, lock_plan
from peagen.models import Task, TaskRun


@pytest.mark.unit
def test_lock_plan_same_hash_for_file_and_mapping(tmp_path: Path) -> None:
    plan = {"steps": [{"action": "a"}, {"action": "b"}]}
    plan_file = tmp_path / "plan.yaml"
    plan_file.write_text(yaml.safe_dump(plan, sort_keys=True), encoding="utf-8")
    assert lock_plan(plan_file) == lock_plan(plan)


@pytest.mark.unit
def test_task_chainer_chains_tasks_and_artifacts() -> None:
    chainer = TaskChainer()
    payload = {"foo": 1}
    expected = chain_hash(json.dumps(payload, sort_keys=True).encode())
    assert chainer.add_task(payload) == expected
    expected = chain_hash(b"artifact", expected)
    assert chainer.add_artifact(b"artifact") == expected
    assert chainer.current_hash == expected


@pytest.mark.unit
def test_taskrun_from_task_includes_hashes() -> None:
    task = Task(pool="p", payload={}, lock_hash="L", chain_hash="C")
    tr = TaskRun.from_task(task)
    assert tr.lock_hash == "L"
    assert tr.chain_hash == "C"
