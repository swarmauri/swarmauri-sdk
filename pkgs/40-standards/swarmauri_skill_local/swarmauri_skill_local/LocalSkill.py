from typing import Literal

from pydantic import ConfigDict

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.FileSystemSkillMixin import FileSystemSkillMixin
from swarmauri_base.skills.LocalSkillMixin import LocalSkillMixin
from swarmauri_base.skills.SkillBase import SkillBase


@ComponentBase.register_type(SkillBase, "LocalSkill")
class LocalSkill(LocalSkillMixin, FileSystemSkillMixin, SkillBase):
    type: Literal["LocalSkill"] = "LocalSkill"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
