from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_tool_listskills import ListSkills
from swarmauri_tool_inspectskill import InspectSkill
from swarmauri_tool_activateskill import ActivateSkill
from swarmauri_tool_readskillresource import ReadSkillResource


@ComponentBase.register_type(ToolkitBase, "SkillsetToolkit")
class SkillsetToolkit(ToolkitBase):
    """Compose skill tools around one host-provided catalog."""

    type: Literal["SkillsetToolkit"] = "SkillsetToolkit"
    catalog: SkillCatalog = Field(exclude=True)

    def model_post_init(self, context):
        self.add_tools(
            {
                "ListSkills": ListSkills(catalog=self.catalog),
                "InspectSkill": InspectSkill(catalog=self.catalog),
                "ActivateSkill": ActivateSkill(catalog=self.catalog),
                "ReadSkillResource": ReadSkillResource(catalog=self.catalog),
            }
        )

    def available_tools(self):
        """Return skill operations and currently activated plugin tools."""
        return {**self.catalog.active, **self.tools}
