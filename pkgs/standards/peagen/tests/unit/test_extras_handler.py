import pytest
from pathlib import Path

from peagen.handlers import extras_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "templates_root, schemas_dir",
    [(None, None), ("/tmp/tmpl", "/tmp/schema")],
)
async def test_extras_handler_calls_generate_schemas(
    monkeypatch, templates_root, schemas_dir
):
    called = {}

    def fake_generate_schemas(t_root: Path, s_dir: Path):
        called["templates_root"] = t_root
        called["schemas_dir"] = s_dir
        return [Path("a"), Path("b")]

    monkeypatch.setattr(handler, "generate_schemas", fake_generate_schemas)

    args = {}
    if templates_root:
        args["templates_root"] = templates_root
    if schemas_dir:
        args["schemas_dir"] = schemas_dir

    task = TaskRead.model_construct(
        id=str(uuid.uuid4()),
        tenant_id=uuid.uuid4(),
        git_reference_id=None,
        pool="default",
        payload={"args": args},
        status=Status.queued,
        note=None,
        spec_hash="",
        date_created=datetime.now(timezone.utc),
        last_modified=datetime.now(timezone.utc),
    )
    result = await handler.extras_handler(task)

    base = Path(handler.__file__).resolve().parents[1]
    expected_templates = (
        Path(templates_root).expanduser() if templates_root else base / "template_sets"
    )
    expected_schemas = (
        Path(schemas_dir).expanduser()
        if schemas_dir
        else base / "jsonschemas" / "extras"
    )

    assert called["templates_root"] == expected_templates
    assert called["schemas_dir"] == expected_schemas
    assert result["generated"] == ["a", "b"]
