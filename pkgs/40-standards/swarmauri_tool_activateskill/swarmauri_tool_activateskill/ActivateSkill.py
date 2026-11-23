from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase


@ComponentBase.register_type(ToolBase, "ActivateSkill")
class ActivateSkill(ToolBase):
    """Load a skill and expose its approved tools."""

    name: str = "ActivateSkill"
    description: str = "Load a skill and expose its approved tools."
    type: Literal["ActivateSkill"] = "ActivateSkill"
    catalog: SkillCatalog = Field(exclude=True)
    parameters: list[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="name",
                input_type="string",
                description="Skill name",
                required=True,
            ),
        ]
    )

    def __call__(self, name: str):
        skill = self.catalog.activate(name)
        return {
            "instructions": skill.instructions,
            "tools": list(self.catalog.active),
        }
