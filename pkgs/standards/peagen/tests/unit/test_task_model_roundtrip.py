import uuid
import pytest

import peagen.gateway as gw
from peagen.models.schemas import TaskCreate, TaskRead
from peagen.orm.task.task import TaskModel


@pytest.mark.unit
def test_task_model_roundtrip() -> None:
    """Ensure TaskCreate → TaskModel → TaskRead → json → TaskRead works."""
    create = TaskCreate(
        id=str(uuid.uuid4()),
        tenant_id=uuid.uuid4(),
        git_reference_id=None,
        parameters={"x": 1},
        note="demo",
    )
    orm = gw.to_orm(create)
    assert isinstance(orm, TaskModel)
    read = gw.to_schema(orm)
    blob = read.model_dump_json()
    again = TaskRead.model_validate_json(blob)
    assert again == read
