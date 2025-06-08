import pytest
from peagen.models.schemas import Task

@pytest.mark.unit
def test_task_labels_deps():
    t = Task(pool="demo", payload={"action": "noop"}, deps=["a"], labels=["x"]) 
    assert t.deps == ["a"]
    assert "x" in t.labels
