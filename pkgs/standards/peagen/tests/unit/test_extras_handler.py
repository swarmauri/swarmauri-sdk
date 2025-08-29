import pytest
from pathlib import Path

from peagen.handlers import extras_handler as handler
from peagen.cli.task_helpers import build_task


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "templates_root, schemas_dir",
    [(None, None), ("/tmp/tmpl", "/tmp/schema")],
)
async def test_extras_handler_calls_generate_schemas(
    monkeypatch, tmp_path, templates_root, schemas_dir
):
    called = {}

    def fake_generate_schemas(t_root: Path, s_dir: Path):
        called["templates_root"] = t_root
        called["schemas_dir"] = s_dir
        return [Path("a"), Path("b")]

    monkeypatch.setattr(handler, "generate_schemas", fake_generate_schemas)

    args = {"worktree": str(tmp_path)}
    if templates_root:
        args["templates_root"] = templates_root
    if schemas_dir:
        args["schemas_dir"] = schemas_dir

    task = build_task(
        action="extras",
        args=args,
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    result = await handler.extras_handler(task)

    base = Path(args["worktree"])
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
