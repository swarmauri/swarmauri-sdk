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
