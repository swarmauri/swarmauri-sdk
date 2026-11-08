from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_base.tools.ToolBase import ToolBase


@ComponentBase.register_type(ToolBase, "ListSkills")
class ListSkills(ToolBase):
    """List available skills."""

    name: str = "ListSkills"
    description: str = "List available skills."
    type: Literal["ListSkills"] = "ListSkills"
    catalog: SkillCatalog = Field(exclude=True)

    def __call__(self):
        return [
            {"name": skill.name, "description": skill.description}
            for skill in self.catalog.skills.values()
        ]
