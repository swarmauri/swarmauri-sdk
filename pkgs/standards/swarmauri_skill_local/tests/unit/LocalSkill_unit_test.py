from swarmauri_skill_local import LocalSkill


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
