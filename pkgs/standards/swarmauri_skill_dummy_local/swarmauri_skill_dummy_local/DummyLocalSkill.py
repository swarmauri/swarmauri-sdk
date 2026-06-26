from __future__ import annotations

from importlib.resources import as_file, files
from typing import ClassVar, Literal

from pydantic import ConfigDict

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.skills.FileSystemSkillMixin import FileSystemSkillMixin
from swarmauri_base.skills.LocalSkillMixin import LocalSkillMixin
from swarmauri_base.skills.SkillBase import SkillBase


@ComponentBase.register_type(SkillBase, "DummyLocalSkill")
class DummyLocalSkill(LocalSkillMixin, FileSystemSkillMixin, SkillBase):
    name: str = "dummy-local"
    description: str = "Dummy local skill for Swarmauri tests."
    instructions: str = "Use this dummy local skill in tests."
    type: Literal["DummyLocalSkill"] = "DummyLocalSkill"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    _DEFAULT_SKILL_NAME: ClassVar[str] = "dummy-local"
    _DEFAULT_SKILLS_ROOT: ClassVar[str] = "skills"

    @classmethod
    def from_default(cls) -> "DummyLocalSkill":
        skills_root = files(__package__).joinpath(cls._DEFAULT_SKILLS_ROOT)
        with as_file(skills_root) as path:
            return cls.from_name(cls._DEFAULT_SKILL_NAME, roots=[path])

    def run_dummy(self, input_text: str = "") -> str:
        normalized_input = " ".join(input_text.strip().split()) or "<empty>"
        resource_count = sum(
            len(getattr(self, field_name))
            for field_name in self._RESOURCE_FIELDS
        )
        return (
            f"{self.skill_name or self.name}|local|resources={resource_count}|"
            f"input={normalized_input}"
        )
