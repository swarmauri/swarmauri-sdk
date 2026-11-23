from typing import Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase


@ComponentBase.register_type(ToolBase, "ReadSkillResource")
class ReadSkillResource(ToolBase):
    """Read a declared skill resource."""

    name: str = "ReadSkillResource"
    description: str = "Read a declared skill resource."
    type: Literal["ReadSkillResource"] = "ReadSkillResource"
    catalog: SkillCatalog = Field(exclude=True)
    parameters: list[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="name",
                input_type="string",
                description="Skill name",
                required=True,
            ),
            ParameterBase(
                name="path",
                input_type="string",
                description="Relative resource path",
                required=True,
            ),
        ]
    )

    def __call__(self, name: str, path: str):
        return {"content": self.catalog.read(name, path).decode("utf-8")}
