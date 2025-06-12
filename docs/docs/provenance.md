# Provenance Tracking

The gateway persists provenance information in four append-only tables:
`task_revision`, `artefact_lineage`, `fanout_set`, and `status_log`.
Each table records immutable facts about task execution.

## API Layer

All writes to these tables are routed through helpers in
`peagen.db.api`.  The helpers accept typed dataclass instances and
perform parameterized inserts using the gateway or worker's database
session.  Any attempt to update or delete rows raises an error at the
database layer.

Example usage:

```python
from peagen.db.models import TaskRevision
from peagen.db.api import insert_task_revision

# assuming `session` is an `AsyncSession`
revision = TaskRevision(rev_hash="abc123", task_id=task_id)
await insert_task_revision(session, revision)
```

If a child revision references a parent hash that does not exist,
`PeagenHashMismatchError` is raised.
