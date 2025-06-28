import uuid
import datetime

import pytest

from peagen.schemas import TaskCreate, TaskDelete, TaskRead, TaskUpdate
from peagen.orm.status import Status


@pytest.mark.unit
def test_task_roundtrip_json(monkeypatch):
    class StubPM:
        def __init__(self, cfg):
            pass

        def get(self, group):
            return None

    import peagen.plugins

    monkeypatch.setattr(peagen.plugins, "PluginManager", StubPM)
    import importlib
    import peagen.gateway as gw

    importlib.reload(gw)

    from peagen.gateway import to_orm

    create = TaskCreate(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        git_reference_id=uuid.uuid4(),
        pool="default",
        payload={"foo": "bar"},
        status=Status.queued,
        note="demo",
        spec_hash="dummy",
        last_modified=datetime.datetime.now(datetime.timezone.utc),
    )
    model = to_orm(create)
    model.date_created = datetime.datetime.now(datetime.timezone.utc)
    model.last_modified = model.date_created
    read = TaskRead.model_validate(model, from_attributes=True)
    dumped = read.model_dump_json()
    restored = TaskRead.model_validate_json(dumped)
    assert restored == read


@pytest.mark.unit
def test_task_schema_fields():
    # TaskCreate includes id and last_modified but not date_created
    assert "id" in TaskCreate.model_fields
    assert "last_modified" in TaskCreate.model_fields
    assert "date_created" not in TaskCreate.model_fields

    # TaskUpdate excludes id and date_created
    assert "id" not in TaskUpdate.model_fields
    assert "date_created" not in TaskUpdate.model_fields

    # TaskRead includes date_created
    assert "date_created" in TaskRead.model_fields

    # TaskDelete requires only id
    assert set(TaskDelete.model_fields) == {"id"}
