import sys
from importlib.metadata import entry_points, version

import pytest

from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_skill_dummy_filesystem import DummyFileSystemSkill
from swarmauri_tool_skill_execution import SkillExecutionTool


def test_version_metadata():
    assert version("swarmauri_tool_skill_execution")


def test_component_identity():
    skill = DummyFileSystemSkill.from_default()
    tool = SkillExecutionTool(skills=[skill])
    dumped = tool.model_dump(mode="json")

    assert tool.resource == ResourceTypes.TOOL.value
    assert tool.type == "SkillExecutionTool"
    assert dumped["resource"] == "Tool"
    assert dumped["type"] == "SkillExecutionTool"
    assert dumped["skills"][0]["resource"] == "Skill"
    assert dumped["skills"][0]["type"] == "DummyFileSystemSkill"
    assert all(
        parameter["resource"] == "Parameter" for parameter in dumped["parameters"]
    )
    assert {parameter["name"] for parameter in dumped["parameters"]} == {
        "skill_name",
        "commands",
        "input_text",
        "timeout",
        "mode",
    }


def test_roundtrip_preserves_skills_parameters_and_behavior():
    skill = DummyFileSystemSkill.from_default()
    tool = SkillExecutionTool(skills=[skill])

    restored = SkillExecutionTool.model_validate_json(tool.model_dump_json())
    result = restored(skill.name, [[sys.executable, "scripts/check.py"]])

    assert restored.resource == "Tool"
    assert restored.type == "SkillExecutionTool"
    assert restored.skills[0].resource == "Skill"
    assert restored.skills[0].type == "DummyFileSystemSkill"
    assert {parameter.name for parameter in restored.parameters} == {
        "skill_name",
        "commands",
        "input_text",
        "timeout",
        "mode",
    }
    assert result["results"][0]["exit_code"] == 0
    assert result["results"][0]["stdout"].strip() == "dummy filesystem skill"


def test_entry_point_loads_skill_execution_tool():
    matches = [
        entry_point
        for entry_point in entry_points(group="swarmauri.tools")
        if entry_point.name == "SkillExecutionTool"
    ]

    assert matches
    assert matches[0].load() is SkillExecutionTool


def test_runs_single_skill_command():
    skill = DummyFileSystemSkill.from_default()
    tool = SkillExecutionTool(skills=[skill])

    result = tool(skill.name, [[sys.executable, "scripts/check.py"]])

    assert result["skill_name"] == "dummy-filesystem"
    assert result["results"][0]["exit_code"] == 0
    assert result["results"][0]["stdout"].strip() == "dummy filesystem skill"


def test_runs_multiple_commands_sequentially():
    skill = DummyFileSystemSkill.from_default()
    tool = SkillExecutionTool(skills=[skill])

    result = tool(
        skill.name,
        [
            [sys.executable, "-c", "print('first')"],
            [sys.executable, "-c", "print('second')"],
        ],
    )

    assert [item["stdout"].strip() for item in result["results"]] == [
        "first",
        "second",
    ]


def test_runs_multiple_commands_concurrently():
    skill = DummyFileSystemSkill.from_default()
    tool = SkillExecutionTool(skills=[skill])

    result = tool(
        skill.name,
        [
            [sys.executable, "-c", "print('first')"],
            [sys.executable, "-c", "print('second')"],
        ],
        mode="concurrent",
    )

    assert result["mode"] == "concurrent"
    assert sorted(item["stdout"].strip() for item in result["results"]) == [
        "first",
        "second",
    ]


def test_passes_input_to_command_stdin():
    skill = DummyFileSystemSkill.from_default()
    tool = SkillExecutionTool(skills=[skill])

    result = tool(
        skill.name,
        [[sys.executable, "-c", "import sys; print(sys.stdin.read().upper())"]],
        input_text="hello",
    )

    assert result["results"][0]["stdout"].strip() == "HELLO"


def test_rejects_shell_string_commands():
    skill = DummyFileSystemSkill.from_default()
    tool = SkillExecutionTool(skills=[skill])

    with pytest.raises(ValueError, match="argv arrays"):
        tool(skill.name, "python scripts/check.py")


def test_timeout_returns_structured_result():
    skill = DummyFileSystemSkill.from_default()
    tool = SkillExecutionTool(skills=[skill])

    result = tool(
        skill.name,
        [[sys.executable, "-c", "import time; time.sleep(1)"]],
        timeout=0.01,
    )

    assert result["results"][0]["exit_code"] == "timeout"
    assert "timed out" in result["results"][0]["stderr"].lower()


def test_unknown_skill_raises():
    tool = SkillExecutionTool()

    with pytest.raises(ValueError, match="Unknown skill"):
        tool("missing", [[sys.executable, "-c", "print('no')"]])


def test_skill_without_root_path_raises():
    skill = DummyFileSystemSkill()
    tool = SkillExecutionTool(skills=[skill])

    with pytest.raises(ValueError, match="root_path"):
        tool(skill.name, [[sys.executable, "-c", "print('no')"]])
