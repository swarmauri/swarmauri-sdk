from pathlib import Path

from swarmauri_skill_local import LocalSkill


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_resolves_golden_local_skill_fixture():
    skill = LocalSkill.from_name("golden-local", roots=[FIXTURES / "skills"])

    assert skill.name == "golden-local"
    assert skill.skill_name == "golden-local"
    assert skill.description == "Golden local skill fixture"
    assert (
        skill.instructions
        == "Use this local fixture to verify named skill resolution."
    )
    assert skill.references == ["references/guide.md"]
    assert skill.type == "LocalSkill"


def test_resolves_skill_from_roots(tmp_path):
    root = tmp_path / "skills"
    skill_dir = root / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: demo
description: Demo
---
Body""",
        encoding="utf-8",
    )

    skill = LocalSkill.from_name("demo", roots=[root])

    assert skill.name == "demo"
    assert skill.skill_name == "demo"
    assert skill.instructions == "Body"


def test_discovers_metadata_from_skill_roots(tmp_path):
    root = tmp_path / "skills"
    skill_dir = root / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: demo
description: Demo skill
---
Body""",
        encoding="utf-8",
    )

    records = LocalSkill.discover([root])

    assert [(record.name, record.description) for record in records] == [
        ("demo", "Demo skill")
    ]


def test_discovery_reports_duplicate_skill_names(tmp_path):
    roots = [tmp_path / "one", tmp_path / "two"]
    for root in roots:
        skill_dir = root / "demo"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            """---
name: demo
description: Demo skill
---
Body""",
            encoding="utf-8",
        )

    import pytest

    with pytest.raises(ValueError, match="Duplicate skill name"):
        LocalSkill.discover(roots)
