from pathlib import Path

from swarmauri_skill_filesystem import FileSystemSkill


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_loads_golden_filesystem_fixture():
    skill = FileSystemSkill.from_path(FIXTURES / "golden-filesystem")

    assert skill.name == "golden-filesystem"
    assert skill.description == "Golden filesystem skill fixture from manifest"
    assert skill.instructions == (
        "Use this filesystem fixture to verify skill package hydration."
    )
    assert skill.metadata == {
        "tags": "manifest filesystem",
        "triggers": "manifest filesystem fixture",
    }
    assert skill.references == ["references/guide.md"]
    assert skill.scripts == ["scripts/check.py"]
    assert skill.assets == []
    assert skill.type == "FileSystemSkill"
    assert skill.root_path == str((FIXTURES / "golden-filesystem").resolve())


def test_loads_skill_markdown_with_frontmatter(tmp_path):
    skill_dir = tmp_path / "demo"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "references" / "guide.md").write_text("ref", encoding="utf-8")
    (skill_dir / "scripts" / "run.py").write_text(
        "print('ok')", encoding="utf-8"
    )
    (skill_dir / "SKILL.md").write_text(
        """---
name: demo
description: Demo skill
---
Use this skill.""",
        encoding="utf-8",
    )

    skill = FileSystemSkill.from_path(skill_dir)

    assert skill.name == "demo"
    assert skill.description == "Demo skill"
    assert skill.instructions == "Use this skill."
    assert skill.references == ["references/guide.md"]
    assert skill.scripts == ["scripts/run.py"]


def test_skill_yaml_overrides_frontmatter(tmp_path):
    skill_dir = tmp_path / "manifest"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        """---
name: front
description: Front
---
Body""",
        encoding="utf-8",
    )
    (skill_dir / "skill.yaml").write_text(
        """name: manifest
description: Manifest
""",
        encoding="utf-8",
    )

    skill = FileSystemSkill.from_path(skill_dir)

    assert skill.name == "manifest"
    assert skill.description == "Manifest"


def test_preserves_additional_bundle_files(tmp_path):
    skill_dir = tmp_path / "demo"
    (skill_dir / "tools").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: demo
description: Demo
---
Body""",
        encoding="utf-8",
    )
    (skill_dir / "tools" / "extra.txt").write_text("bad", encoding="utf-8")

    skill = FileSystemSkill.from_path(skill_dir)
    assert FileSystemSkill.load_resource(skill, "tools/extra.txt") == b"bad"
