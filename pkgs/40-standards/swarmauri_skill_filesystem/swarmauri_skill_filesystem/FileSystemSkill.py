from typing import Literal

from pydantic import ConfigDict

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.FileSystemSkillMixin import FileSystemSkillMixin
from swarmauri_base.skills.SkillBase import SkillBase


@ComponentBase.register_type(SkillBase, "FileSystemSkill")
class FileSystemSkill(FileSystemSkillMixin, SkillBase):
    type: Literal["FileSystemSkill"] = "FileSystemSkill"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
