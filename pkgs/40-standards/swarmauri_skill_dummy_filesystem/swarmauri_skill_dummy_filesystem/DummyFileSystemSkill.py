from __future__ import annotations

from importlib.resources import as_file, files
from typing import ClassVar, Literal

from pydantic import ConfigDict

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.FileSystemSkillMixin import FileSystemSkillMixin
from swarmauri_base.skills.SkillBase import SkillBase


@ComponentBase.register_type(SkillBase, "DummyFileSystemSkill")
class DummyFileSystemSkill(FileSystemSkillMixin, SkillBase):
    name: str = "dummy-filesystem"
    description: str = "Dummy filesystem skill for Swarmauri tests."
    instructions: str = "Use this dummy filesystem skill in tests."
    type: Literal["DummyFileSystemSkill"] = "DummyFileSystemSkill"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    _DEFAULT_SKILL_DIR: ClassVar[str] = "skills/dummy-filesystem"

    @classmethod
    def from_default(cls) -> "DummyFileSystemSkill":
        skill_root = files(__package__).joinpath(cls._DEFAULT_SKILL_DIR)
        with as_file(skill_root) as path:
            return cls.from_path(path)

    def run_dummy(self, input_text: str = "") -> str:
        normalized_input = " ".join(input_text.strip().split()) or "<empty>"
        resource_count = sum(
            len(getattr(self, field_name))
            for field_name in self._RESOURCE_FIELDS
        )
        return (
            f"{self.name}|filesystem|resources={resource_count}|"
            f"input={normalized_input}"
        )
