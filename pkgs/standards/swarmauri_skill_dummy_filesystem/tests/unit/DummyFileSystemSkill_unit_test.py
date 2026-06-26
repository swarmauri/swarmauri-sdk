from importlib.metadata import entry_points, version

from swarmauri_base.DynamicBase import DynamicBase
from swarmauri_base.skills import FileSystemSkillMixin, SkillBase
from swarmauri_skill_dummy_filesystem import DummyFileSystemSkill


def test_version_metadata():
    assert version("swarmauri_skill_dummy_filesystem")


def test_dummy_filesystem_skill_defaults():
    skill = DummyFileSystemSkill()

    assert isinstance(skill, SkillBase)
    assert isinstance(skill, FileSystemSkillMixin)
    assert skill.name == "dummy-filesystem"
    assert skill.type == "DummyFileSystemSkill"


def test_dummy_filesystem_skill_registers_under_skill_base():
    assert (
        DynamicBase._registry["SkillBase"]["subtypes"]["DummyFileSystemSkill"]
        is DummyFileSystemSkill
    )


def test_dummy_filesystem_skill_loads_packaged_skill():
    skill = DummyFileSystemSkill.from_default()

    assert skill.name == "dummy-filesystem"
    assert skill.description == "Packaged dummy filesystem skill"
    assert skill.references == ["references/guide.md"]
    assert skill.scripts == ["scripts/check.py"]
    assert skill.type == "DummyFileSystemSkill"


def test_dummy_filesystem_skill_has_verifiable_behavior():
    skill = DummyFileSystemSkill.from_default()

    assert (
        skill.run_dummy("  hello   filesystem  ")
        == "dummy-filesystem|filesystem|resources=2|input=hello filesystem"
    )


def test_entry_point_loads_dummy_filesystem_skill():
    matches = [
        entry_point
        for entry_point in entry_points(group="swarmauri.skills")
        if entry_point.name == "DummyFileSystemSkill"
    ]

    assert matches
    assert matches[0].load() is DummyFileSystemSkill
