from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_toolkit_skillset import SkillsetToolkit

toolkit = SkillsetToolkit(catalog=SkillCatalog([]))
print(toolkit.get_tool_by_name("ListSkills")())
