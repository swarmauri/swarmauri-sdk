import uuid
import datetime

import pytest

from peagen.schemas import TaskCreate, TaskRead


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
        parameters={"foo": "bar"},
        note="demo",
    )
    model = to_orm(create)
    model.date_created = datetime.datetime.now(datetime.timezone.utc)
    model.last_modified = model.date_created
    read = TaskRead.model_validate(model, from_attributes=True)
    dumped = read.model_dump_json()
    restored = TaskRead.model_validate_json(dumped)
    assert restored == read
