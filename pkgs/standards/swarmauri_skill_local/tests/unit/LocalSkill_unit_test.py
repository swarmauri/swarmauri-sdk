from pathlib import Path

from swarmauri_skill_local import LocalSkill


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_resolves_golden_local_skill_fixture():
    skill = LocalSkill.from_name("golden-local", roots=[FIXTURES / "skills"])

    assert skill.name == "golden-local"
    assert skill.skill_name == "golden-local"
    assert skill.description == "Golden local skill fixture"
    assert (
        skill.instructions == "Use this local fixture to verify named skill resolution."
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
