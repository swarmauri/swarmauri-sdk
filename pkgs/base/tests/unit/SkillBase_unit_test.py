from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_base.skills import SkillBase


def test_skillbase_parses_markdown_frontmatter():
    skill = SkillBase.from_markdown(
        """---
name: demo
description: Demo
scripts:
  - scripts/run.py
---
Body"""
    )

    assert skill.name == "demo"
    assert skill.description == "Demo"
    assert skill.instructions == "Body"
    assert skill.scripts == ["scripts/run.py"]
    assert skill.resource == ResourceTypes.SKILL.value


def test_skillbase_manifest_overrides_frontmatter():
    skill = SkillBase.from_markdown(
        """---
name: front
description: Front
---
Body""",
        manifest={"name": "manifest", "description": "Manifest"},
    )

    assert skill.name == "manifest"
    assert skill.description == "Manifest"


def test_skillbase_accepts_standard_resource_extensions():
    skill = SkillBase(
        name="bad",
        description="Bad",
        instructions="Body",
        references=["references/bad.txt"],
    )
    assert skill.references == ["references/bad.txt"]
