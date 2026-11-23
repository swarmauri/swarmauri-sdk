from swarmauri_skill_dummy_filesystem import DummyFileSystemSkill
from swarmauri_tool_skill_execution import SkillExecutionTool

skill = DummyFileSystemSkill.from_default()
tool = SkillExecutionTool(skills=[skill])
result = tool(skill.name, [["python", "scripts/check.py"]])
print(result["results"][0]["stdout"])
