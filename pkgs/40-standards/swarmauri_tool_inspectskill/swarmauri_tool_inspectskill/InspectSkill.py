from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase


@ComponentBase.register_type(ToolBase, "InspectSkill")
class InspectSkill(ToolBase):
    """Inspect metadata for a named skill."""

    name: str = "InspectSkill"
    description: str = "Inspect metadata for a named skill."
    type: Literal["InspectSkill"] = "InspectSkill"
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
        skill = self.catalog.skills[name]
        return skill.model_dump(mode="json", exclude={"instructions"})
