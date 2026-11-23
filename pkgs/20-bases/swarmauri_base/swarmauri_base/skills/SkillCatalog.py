from collections.abc import Callable, Iterable, Mapping

from swarmauri_base.tools.ToolBase import ToolBase

from .SkillBase import SkillBase


class SkillCatalog:
    """Resolve skill instructions, resources, and approved tool factories."""

    def __init__(
        self,
        skills: Iterable[SkillBase],
        *,
        factories: Mapping[str, Callable[[], ToolBase]] | None = None,
    ):
        self.skills: dict[str, SkillBase] = {}
        for skill in skills:
            if skill.name in self.skills:
                raise ValueError(f"Duplicate skill name: {skill.name}")
            self.skills[skill.name] = skill
        self.factories = dict(factories or {})
        self.active: dict[str, ToolBase] = {}

    def activate(self, name: str) -> SkillBase:
        skill = self.skills[name]
        for tool_name in skill.allowed_tools:
            if tool_name in self.factories and tool_name not in self.active:
                tool = self.factories[tool_name]()
                if tool.name != tool_name:
                    raise ValueError(
                        f"Factory returned the wrong tool for {tool_name}"
                    )
                self.active[tool_name] = tool
        return skill

    def read(self, name: str, path: str) -> bytes:
        skill = self.skills[name]
        if path not in (*skill.references, *skill.assets, *skill.scripts):
            raise ValueError("Resource is not declared by the skill")
        return skill.read_resource(path)
