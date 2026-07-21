from typing import Literal

import pytest
from pydantic import ConfigDict

from swarmauri_base.skills import (
    FileSystemSkillMixin,
    LocalSkillMixin,
    SkillBase,
)


class MixinSkill(LocalSkillMixin, FileSystemSkillMixin, SkillBase):
    type: Literal["MixinSkill"] = "MixinSkill"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


def _write_skill(skill_dir, body="Body"):
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: demo
description: Demo skill
---
{body}""",
        encoding="utf-8",
    )


def test_filesystem_skill_mixin_loads_skill_package(tmp_path):
    skill_dir = tmp_path / "demo"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "references" / "guide.md").write_text("ref", encoding="utf-8")
    _write_skill(skill_dir)

    skill = MixinSkill.from_path(skill_dir)

    assert skill.name == "demo"
    assert skill.root_path == str(skill_dir.resolve())
    assert skill.references == ["references/guide.md"]


def test_local_skill_mixin_resolves_named_skill(tmp_path):
    root = tmp_path / "skills"
    _write_skill(root / "demo")

    skill = MixinSkill.from_name("demo", roots=[root])

    assert skill.name == "demo"
    assert skill.skill_name == "demo"


def test_local_skill_mixin_raises_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        MixinSkill.from_name("missing", roots=[tmp_path])


def test_discover_returns_metadata_without_activating_resources(tmp_path):
    skill_dir = tmp_path / "demo"
    _write_skill(skill_dir)
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "guide.md").write_text("ref", encoding="utf-8")

    records = MixinSkill.discover(skill_dir)

    assert len(records) == 1
    assert records[0].name == "demo"
    assert records[0].description == "Demo skill"
    assert records[0].location == str(skill_dir.resolve())
    assert not hasattr(records[0], "instructions")


def test_load_resource_is_lazy_and_root_contained(tmp_path):
    skill_dir = tmp_path / "demo"
    _write_skill(skill_dir)
    (skill_dir / "assets").mkdir()
    (skill_dir / "assets" / "data.bin").write_bytes(b"payload")
    skill = MixinSkill.from_path(skill_dir)

    assert skill.assets == ["assets/data.bin"]
    assert skill.read_resource("assets/data.bin") == b"payload"
    with pytest.raises(ValueError, match="escapes"):
        skill.read_resource("../outside")


def test_skillbase_accepts_standard_metadata_and_bom():
    skill = SkillBase.from_markdown(
        "\ufeff---\n"
        "name: data-analysis\n"
        "description: Analyze data and report findings.\n"
        "license: Apache-2.0\n"
        "compatibility: Requires Python 3.12\n"
        "allowed-tools: Read Bash\n"
        "assets: [assets/template.csv]\n"
        "---\n"
        "Instructions"
    )

    assert skill.license == "Apache-2.0"
    assert skill.compatibility == "Requires Python 3.12"
    assert skill.allowed_tools == ["Read", "Bash"]
    assert skill.assets == ["assets/template.csv"]


def test_discover_merges_skill_yaml_manifest(tmp_path):
    skill_dir = tmp_path / "demo"
    _write_skill(skill_dir)
    (skill_dir / "skill.yaml").write_text(
        """name: demo
description: Manifest description
metadata:
  triggers: manifest-trigger
""",
        encoding="utf-8",
    )

    record = MixinSkill.discover(skill_dir)[0]

    assert record.description == "Manifest description"
    assert record.metadata == {"triggers": "manifest-trigger"}
