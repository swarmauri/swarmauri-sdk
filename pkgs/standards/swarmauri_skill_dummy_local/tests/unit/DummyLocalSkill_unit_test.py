from importlib.metadata import entry_points, version

from pydantic import BaseModel

from swarmauri_base.ComponentBase import SubclassUnion
from swarmauri_base.DynamicBase import DynamicBase
from swarmauri_base.skills import FileSystemSkillMixin, LocalSkillMixin, SkillBase
from swarmauri_skill_dummy_local import DummyLocalSkill


class SkillEnvelope(BaseModel):
    skill: SubclassUnion[SkillBase]


def resource_value(component):
    resource = component.resource
    return getattr(resource, "value", resource)


def test_version_metadata():
    assert version("swarmauri_skill_dummy_local")


def test_dummy_local_skill_defaults():
    skill = DummyLocalSkill()

    assert isinstance(skill, SkillBase)
    assert isinstance(skill, LocalSkillMixin)
    assert isinstance(skill, FileSystemSkillMixin)
    assert skill.name == "dummy-local"
    assert skill.type == "DummyLocalSkill"


def test_dummy_local_skill_component_identity():
    skill = DummyLocalSkill.from_default()
    dumped = skill.model_dump(mode="json")

    assert resource_value(skill) == "Skill"
    assert skill.type == "DummyLocalSkill"
    assert dumped["resource"] == "Skill"
    assert dumped["type"] == "DummyLocalSkill"
    assert dumped["name"] == "dummy-local"


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


def test_dummy_local_skill_roundtrip_preserves_identity_and_fields():
    skill = DummyLocalSkill.from_default()

    restored = DummyLocalSkill.model_validate_json(skill.model_dump_json())

    assert restored.type == "DummyLocalSkill"
    assert resource_value(restored) == "Skill"
    assert restored.name == skill.name
    assert restored.skill_name == skill.skill_name
    assert restored.description == skill.description
    assert restored.instructions == skill.instructions
    assert restored.metadata == skill.metadata
    assert restored.references == skill.references
    assert restored.root_path == skill.root_path


def test_dummy_local_skill_base_roundtrip_preserves_subclass_type():
    skill = DummyLocalSkill.from_default()

    restored = SkillEnvelope.model_validate({"skill": skill.model_dump(mode="json")})

    assert isinstance(restored.skill, DummyLocalSkill)
    assert restored.skill.type == "DummyLocalSkill"
    assert resource_value(restored.skill) == "Skill"


def test_dummy_local_skill_has_verifiable_behavior():
    skill = DummyLocalSkill.from_default()

    assert (
        skill.run_dummy("  hello   local  ")
        == "dummy-local|local|resources=1|input=hello local"
    )


def test_dummy_local_skill_roundtrip_preserves_behavior():
    skill = DummyLocalSkill.from_default()
    restored = DummyLocalSkill.model_validate_json(skill.model_dump_json())

    assert restored.run_dummy("  hello   local  ") == skill.run_dummy(
        "  hello   local  "
    )


def test_entry_point_loads_dummy_local_skill():
    matches = [
        entry_point
        for entry_point in entry_points(group="swarmauri.skills")
        if entry_point.name == "DummyLocalSkill"
    ]

    assert matches
    assert matches[0].load() is DummyLocalSkill
