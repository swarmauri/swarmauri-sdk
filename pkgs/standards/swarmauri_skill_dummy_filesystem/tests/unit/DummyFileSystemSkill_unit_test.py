from importlib.metadata import entry_points, version

from pydantic import TypeAdapter

from swarmauri_base.ComponentBase import SubclassUnion
from swarmauri_base.DynamicBase import DynamicBase
from swarmauri_base.skills import FileSystemSkillMixin, SkillBase
from swarmauri_skill_dummy_filesystem import DummyFileSystemSkill


def resource_value(component):
    resource = component.resource
    return getattr(resource, "value", resource)


def test_version_metadata():
    assert version("swarmauri_skill_dummy_filesystem")


def test_dummy_filesystem_skill_defaults():
    skill = DummyFileSystemSkill()

    assert isinstance(skill, SkillBase)
    assert isinstance(skill, FileSystemSkillMixin)
    assert skill.name == "dummy-filesystem"
    assert skill.type == "DummyFileSystemSkill"


def test_dummy_filesystem_skill_component_identity():
    skill = DummyFileSystemSkill.from_default()
    dumped = skill.model_dump(mode="json")

    assert resource_value(skill) == "Skill"
    assert skill.type == "DummyFileSystemSkill"
    assert dumped["resource"] == "Skill"
    assert dumped["type"] == "DummyFileSystemSkill"
    assert dumped["name"] == "dummy-filesystem"


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


def test_dummy_filesystem_skill_roundtrip_preserves_identity_and_fields():
    skill = DummyFileSystemSkill.from_default()

    restored = DummyFileSystemSkill.model_validate_json(skill.model_dump_json())

    assert restored.type == "DummyFileSystemSkill"
    assert resource_value(restored) == "Skill"
    assert restored.name == skill.name
    assert restored.description == skill.description
    assert restored.instructions == skill.instructions
    assert restored.metadata == skill.metadata
    assert restored.references == skill.references
    assert restored.scripts == skill.scripts
    assert restored.root_path == skill.root_path


def test_dummy_filesystem_skill_base_roundtrip_preserves_subclass_type():
    skill = DummyFileSystemSkill.from_default()
    skill_adapter = TypeAdapter(SubclassUnion[SkillBase])

    restored = skill_adapter.validate_json(skill.model_dump_json())

    assert isinstance(restored, DummyFileSystemSkill)
    assert restored.type == "DummyFileSystemSkill"
    assert resource_value(restored) == "Skill"


def test_dummy_filesystem_skill_has_verifiable_behavior():
    skill = DummyFileSystemSkill.from_default()

    assert (
        skill.run_dummy("  hello   filesystem  ")
        == "dummy-filesystem|filesystem|resources=2|input=hello filesystem"
    )


def test_dummy_filesystem_skill_roundtrip_preserves_behavior():
    skill = DummyFileSystemSkill.from_default()
    restored = DummyFileSystemSkill.model_validate_json(skill.model_dump_json())

    assert restored.run_dummy("  hello   filesystem  ") == skill.run_dummy(
        "  hello   filesystem  "
    )


def test_entry_point_loads_dummy_filesystem_skill():
    matches = [
        entry_point
        for entry_point in entry_points(group="swarmauri.skills")
        if entry_point.name == "DummyFileSystemSkill"
    ]

    assert matches
    assert matches[0].load() is DummyFileSystemSkill
