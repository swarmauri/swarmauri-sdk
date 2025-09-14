import uuid
import pytest
from pydantic import BaseModel, Field
import importlib.util
import sys
from pathlib import Path
import tigrbl as tigrbl_v3


class DummyTaskModel(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    pool_id: str
    action: str
    repo: str
    ref: str
    args: dict | None = None
    labels: dict | None = None
    note: str | None = None
    status: str = "waiting"
    repository_id: str | None = None
    config_toml: str | None = None
    spec_kind: str | None = None
    spec_uuid: str | None = None

    @property
    def payload(self):
        return {"action": self.action, "args": self.args or {}}


_orig_get_schema = tigrbl_v3.get_schema


def _dummy_get_schema(orm_cls, op, *, kind="out"):
    if orm_cls.__name__ == "Task":
        return DummyTaskModel
    return _orig_get_schema(orm_cls, op, kind=kind)


tigrbl_v3.get_schema = _dummy_get_schema

spec = importlib.util.spec_from_file_location(
    "peagen.cli.task_helpers",
    Path(__file__).resolve().parents[2] / "peagen" / "cli" / "task_helpers.py",
)
task_helpers = importlib.util.module_from_spec(spec)
sys.modules["peagen.cli.task_helpers"] = task_helpers
spec.loader.exec_module(task_helpers)


@pytest.fixture(autouse=True)
def restore_get_schema():
    yield
    tigrbl_v3.get_schema = _orig_get_schema
