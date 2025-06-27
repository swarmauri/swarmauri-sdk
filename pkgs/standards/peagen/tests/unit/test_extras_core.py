import json
from pathlib import Path
import pytest

from peagen.core.extras_core import parse_keys, build_schema, generate_schemas


@pytest.mark.unit
def test_parse_keys_reads_bullets(tmp_path: Path):
    md = tmp_path / "EXTRAS.md"
    md.write_text("""
Intro
- foo
- bar
-notabullet
- baz
""")
    assert parse_keys(md) == ["foo", "bar", "baz"]


@pytest.mark.unit
def test_build_schema_produces_json_schema():
    schema = build_schema(["one", "two"], "myset")
    assert schema["$id"].endswith("myset.schema.json")
    assert set(schema["properties"]) == {"one", "two"}


@pytest.mark.unit
def test_generate_schemas_creates_files(tmp_path: Path):
    tmpl_root = tmp_path / "tmpl"
    tmpl_root.mkdir()
    (tmpl_root / "set1").mkdir()
    (tmpl_root / "set1" / "EXTRAS.md").write_text("- a\n- b")
    (tmpl_root / "set2").mkdir()
    (tmpl_root / "set2" / "EXTRAS.md").write_text("- c")

    out_dir = tmp_path / "jsonschemas"
    written = generate_schemas(tmpl_root, out_dir)
    assert len(written) == 2
    contents = [json.loads(p.read_text()) for p in written]
    assert all("properties" in c for c in contents)
