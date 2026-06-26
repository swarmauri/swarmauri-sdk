from importlib.metadata import entry_points, version

from swarmauri_base.DynamicBase import DynamicBase
from swarmauri_base.skills import FileSystemSkillMixin, LocalSkillMixin, SkillBase
from swarmauri_skill_dummy_local import DummyLocalSkill


def test_version_metadata():
    assert version("swarmauri_skill_dummy_local")


def test_dummy_local_skill_defaults():
    skill = DummyLocalSkill()

    assert isinstance(skill, SkillBase)
    assert isinstance(skill, LocalSkillMixin)
    assert isinstance(skill, FileSystemSkillMixin)
    assert skill.name == "dummy-local"
    assert skill.type == "DummyLocalSkill"


def test_dummy_local_skill_registers_under_skill_base():
    assert (
        DynamicBase._registry["SkillBase"]["subtypes"]["DummyLocalSkill"]
        is DummyLocalSkill
    )


def test_dummy_local_skill_loads_packaged_skill_by_name():
    skill = DummyLocalSkill.from_default()

    assert skill.name == "dummy-local"
    assert skill.skill_name == "dummy-local"
    assert skill.description == "Packaged dummy local skill"
    assert skill.references == ["references/guide.md"]
    assert skill.type == "DummyLocalSkill"


def test_dummy_local_skill_has_verifiable_behavior():
    skill = DummyLocalSkill.from_default()

    assert (
        skill.run_dummy("  hello   local  ")
        == "dummy-local|local|resources=1|input=hello local"
    )


def test_entry_point_loads_dummy_local_skill():
    matches = [
        entry_point
        for entry_point in entry_points(group="swarmauri.skills")
        if entry_point.name == "DummyLocalSkill"
    ]

    assert matches
    assert matches[0].load() is DummyLocalSkill
