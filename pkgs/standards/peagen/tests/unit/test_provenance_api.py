import uuid
import pytest

from peagen.db.api import (
    insert_task_revision,
    insert_artefact_lineage,
    insert_fanout_set,
    insert_status_log,
)
from peagen.db.errors import PeagenError, PeagenHashMismatchError
from peagen.db.models import (
    ArtefactLineage,
    FanoutSet,
    StatusLog,
    TaskRevision,
)
from peagen.models.schemas import Status
from sqlalchemy.exc import IntegrityError


class DummyResult:
    def __init__(self, value=None):
        self._value = value

    def scalar(self):
        return self._value


class DummySession:
    def __init__(self, parent_exists=True, fail_exc=None):
        self.parent_exists = parent_exists
        self.fail_exc = fail_exc
        self.queries = []
        self.params = []

    async def execute(self, stmt, params):
        self.queries.append(str(stmt))
        self.params.append(params)
        if self.fail_exc:
            raise self.fail_exc
        if "SELECT 1 FROM task_revision" in str(stmt):
            return DummyResult(1 if self.parent_exists else None)
        return DummyResult()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_insert_task_revision_success():
    s = DummySession()
    row = TaskRevision(rev_hash="h1", task_id=uuid.uuid4())
    await insert_task_revision(s, row)
    assert any("INSERT INTO task_revision" in q for q in s.queries)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_insert_task_revision_bad_parent():
    s = DummySession(parent_exists=False)
    row = TaskRevision(rev_hash="h1", task_id=uuid.uuid4(), parent_hash="nope")
    with pytest.raises(PeagenHashMismatchError):
        await insert_task_revision(s, row)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_insert_helpers_propagate_integrity_error():
    exc = IntegrityError("dup", {}, None)
    s = DummySession(fail_exc=exc)
    row = FanoutSet(rev_hash="h1", child_hash="c")
    with pytest.raises(PeagenError):
        await insert_fanout_set(s, row)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_insert_other_tables():
    s = DummySession()
    await insert_artefact_lineage(
        s, ArtefactLineage(edge_hash="e", parent_hash="p", child_hash="c")
    )
    await insert_fanout_set(s, FanoutSet(rev_hash="r", child_hash="c"))
    await insert_status_log(s, StatusLog(rev_hash="r", status=Status.success))
    assert len(s.queries) == 3
