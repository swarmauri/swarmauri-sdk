from __future__ import annotations

import asyncio
import inspect
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
)

from pydantic import ConfigDict, Field, PrivateAttr

from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_base.agents.AgentSystemContextMixin import (
    AgentSystemContextMixin,
)
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.skills.SkillBase import SkillBase
from swarmauri_base.skills.SkillMetadata import SkillMetadata
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.messages.IMessage import IMessage
from swarmauri_core.skills.ISkillLoader import ISkillLoader
from swarmauri_standard.conversations.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_tool_skill_execution import SkillExecutionTool


@ComponentBase.register_type(AgentBase, "SkillAgent")
class SkillAgent(AgentSystemContextMixin, AgentConversationMixin, AgentBase):
    llm: SubclassUnion[LLMBase]
    conversation: SubclassUnion[ConversationBase] = Field(
        default_factory=lambda: MaxSystemContextConversation(
            system_context="", max_size=100
        )
    )
    system_context: SystemMessage | str = SystemMessage(content="")
    skills: List[SubclassUnion[SkillBase]] = Field(default_factory=list)
    skill_metadata: List[SkillMetadata] = Field(default_factory=list)
    skill_loader: ISkillLoader | None = None
    _skill_roots: List[str] = PrivateAttr(default_factory=list)
    skill_execution_tool: SubclassUnion[ToolBase] = Field(
        default_factory=SkillExecutionTool
    )
    turn_mode: Literal["single", "multi"] = "multi"
    execution_mode: Literal["sequential", "concurrent"] = "sequential"
    require_skill: bool = False
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["SkillAgent"] = "SkillAgent"

    def model_post_init(self, __context: Any) -> None:
        self.skills = [self._hydrate_skill(item) for item in self.skills]
        if not self.skill_metadata:
            self.skill_metadata = [
                self._metadata_for_skill(skill) for skill in self.skills
            ]

    @staticmethod
    def _hydrate_skill(value: Any) -> Any:
        if isinstance(value, SkillBase) or not isinstance(value, dict):
            return value
        type_name = value.get("type")
        skill_registry = SkillBase._registry.get("SkillBase", {})
        skill_cls = skill_registry.get("subtypes", {}).get(type_name)
        if skill_cls is None and type_name == "SkillBase":
            skill_cls = skill_registry.get("model_cls", SkillBase)
        return skill_cls.model_validate(value) if skill_cls else value

    def exec(
        self,
        input_str: Optional[
            Union[str, IMessage, Sequence[Union[str, IMessage]]]
        ] = "",
        llm_kwargs: Optional[Dict] = None,
        skill_names: Optional[Sequence[str]] = None,
    ) -> Any:
        inputs = self._normalize_inputs(input_str)
        if len(inputs) == 1:
            return self._exec_one(
                inputs[0], llm_kwargs=llm_kwargs, skill_names=skill_names
            )
        return [
            self._exec_one(
                item, llm_kwargs=llm_kwargs, skill_names=skill_names
            )
            for item in inputs
        ]

    async def aexec(
        self,
        input_str: Optional[
            Union[str, IMessage, Sequence[Union[str, IMessage]]]
        ] = "",
        llm_kwargs: Optional[Dict] = None,
        skill_names: Optional[Sequence[str]] = None,
    ) -> Any:
        inputs = self._normalize_inputs(input_str)
        if len(inputs) == 1:
            return await self._aexec_one(
                inputs[0], llm_kwargs=llm_kwargs, skill_names=skill_names
            )
        if self.execution_mode == "concurrent":
            return await asyncio.gather(
                *[
                    self._aexec_one(
                        item, llm_kwargs=llm_kwargs, skill_names=skill_names
                    )
                    for item in inputs
                ]
            )
        results = []
        for item in inputs:
            results.append(
                await self._aexec_one(
                    item, llm_kwargs=llm_kwargs, skill_names=skill_names
                )
            )
        return results

    @classmethod
    def from_skill_roots(
        cls,
        llm: LLMBase,
        roots: Iterable[str],
        loader_cls: Any,
        **kwargs: Any,
    ) -> "SkillAgent":
        """Discover metadata now and activate only selected skills later."""
        root_list = list(roots)
        metadata = loader_cls.discover(root_list)
        agent = cls(llm=llm, skill_metadata=metadata, **kwargs)
        agent._skill_roots = [str(root) for root in root_list]
        if isinstance(loader_cls, type) and issubclass(loader_cls, SkillBase):
            # Shipped filesystem/local skill classes expose classmethod loader
            # APIs but cannot be instantiated without skill fields.
            agent.skill_loader = loader_cls
        elif isinstance(loader_cls, type):
            agent.skill_loader = loader_cls()
        else:
            agent.skill_loader = loader_cls
        return agent

    @staticmethod
    def _metadata_for_skill(skill: SkillBase) -> SkillMetadata:
        return SkillMetadata(
            name=skill.name,
            description=skill.description,
            license=skill.license,
            compatibility=skill.compatibility,
            metadata=skill.metadata,
            source="loaded",
            location=str(getattr(skill, "root_path", "")),
        )

    def _activate_metadata(
        self, selected_metadata: Sequence[SkillMetadata]
    ) -> List[SkillBase]:
        if not self.skill_loader:
            return [
                skill
                for skill in self.skills
                if skill.name in {item.name for item in selected_metadata}
            ]
        loaded = {skill.name: skill for skill in self.skills}
        for metadata in selected_metadata:
            if metadata.name in loaded:
                continue
            if hasattr(self.skill_loader, "from_name"):
                skill = self.skill_loader.from_name(
                    metadata.name, roots=self._skill_roots
                )
            else:
                skill = self.skill_loader.load(
                    metadata.location, skill_name=metadata.name
                )
            loaded[metadata.name] = skill
            self.skills.append(skill)
        return [loaded[item.name] for item in selected_metadata]

    def select_skills(
        self,
        input_data: Union[str, IMessage],
        skill_names: Optional[Sequence[str]] = None,
    ) -> List[SkillBase]:
        catalog = self.skill_metadata
        if skill_names:
            requested = set(skill_names)
            selected_metadata = [
                item for item in catalog if item.name in requested
            ]
            missing = sorted(
                requested - {item.name for item in selected_metadata}
            )
            if missing:
                raise ValueError(
                    f"Unknown skill name(s): {', '.join(missing)}"
                )
            return self._activate_metadata(selected_metadata)

        if len(catalog) == 1:
            return self._activate_metadata(catalog)

        input_text = self._input_text(input_data).lower()
        selected_metadata = [
            item
            for item in catalog
            if self._skill_matches_input(item, input_text)
        ]
        if not selected_metadata and self.require_skill:
            raise ValueError("No matching skill found for input")
        return self._activate_metadata(selected_metadata)

    def _exec_one(
        self,
        input_data: Union[str, IMessage],
        llm_kwargs: Optional[Dict] = None,
        skill_names: Optional[Sequence[str]] = None,
    ) -> Any:
        conversation, selected_skills = self._prepare_conversation(
            input_data, skill_names=skill_names
        )
        result = self.llm.predict(
            conversation=conversation,
            **self._llm_kwargs(selected_skills, llm_kwargs),
        )
        if result is not None:
            conversation = result
        if self.turn_mode == "multi":
            self.conversation = conversation
        return conversation.get_last().content

    async def _aexec_one(
        self,
        input_data: Union[str, IMessage],
        llm_kwargs: Optional[Dict] = None,
        skill_names: Optional[Sequence[str]] = None,
    ) -> Any:
        conversation, selected_skills = self._prepare_conversation(
            input_data, skill_names=skill_names
        )
        result = await self.llm.apredict(
            conversation=conversation,
            **self._llm_kwargs(
                selected_skills, llm_kwargs, method_name="apredict"
            ),
        )
        if result is not None:
            conversation = result
        if self.turn_mode == "multi":
            self.conversation = conversation
        return conversation.get_last().content

    def _prepare_conversation(
        self,
        input_data: Union[str, IMessage],
        skill_names: Optional[Sequence[str]] = None,
    ) -> tuple[ConversationBase, List[SkillBase]]:
        conversation = self.conversation
        if self.turn_mode == "single":
            conversation = self.conversation.model_copy(deep=True)
            conversation.clear_history()

        selected_skills = self.select_skills(
            input_data, skill_names=skill_names
        )
        self._apply_system_context(conversation, selected_skills)
        conversation.add_message(self._to_message(input_data))
        return conversation, selected_skills

    def _apply_system_context(
        self,
        conversation: ConversationBase,
        selected_skills: Iterable[SkillBase],
    ) -> None:
        context_parts = [self.system_context.content]
        skill_context = self._build_skill_context(selected_skills)
        if skill_context:
            context_parts.append(skill_context)
        system_context = "\n\n".join(part for part in context_parts if part)
        if hasattr(conversation, "system_context"):
            conversation.system_context = SystemMessage(content=system_context)
        elif system_context:
            conversation.add_message(SystemMessage(content=system_context))

    def execute_skill_commands(
        self,
        skill_name: str,
        commands: Sequence[Sequence[str]] | Sequence[str],
        input_text: str | None = None,
        timeout: float | None = None,
        mode: Literal["sequential", "concurrent"] = "sequential",
    ) -> Dict[str, Any]:
        self.skill_execution_tool.skills = list(self.skills)
        return self.skill_execution_tool(
            skill_name=skill_name,
            commands=commands,
            input_text=input_text,
            timeout=timeout,
            mode=mode,
        )

    def get_skill_toolkit(
        self, skills: Optional[Iterable[SkillBase]] = None
    ) -> Toolkit:
        selected_skills = list(skills if skills is not None else self.skills)
        self.skill_execution_tool.skills = selected_skills
        toolkit = Toolkit()
        toolkit.add_tool(self.skill_execution_tool)
        return toolkit

    def load_skill_resource(
        self, skill_name: str, relative_path: str
    ) -> bytes:
        """Load one selected skill resource without eager context injection."""
        for skill in self.skills:
            if skill.name == skill_name:
                reader = getattr(skill, "read_resource", None)
                if reader is None:
                    raise ValueError(
                        f"Skill '{skill_name}' does not support "
                        "filesystem resources"
                    )
                return reader(relative_path)
        raise ValueError(f"Unknown skill name: {skill_name}")

    def _llm_kwargs(
        self,
        selected_skills: Iterable[SkillBase],
        llm_kwargs: Optional[Dict],
        method_name: str = "predict",
    ) -> Dict:
        kwargs = dict(llm_kwargs or {})
        method = getattr(self.llm, method_name)
        signature = inspect.signature(method)
        accepts_kwargs = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )
        if "toolkit" in signature.parameters or accepts_kwargs:
            kwargs.setdefault(
                "toolkit", self.get_skill_toolkit(selected_skills)
            )
        return kwargs

    @classmethod
    def _build_skill_context(cls, skills: Iterable[SkillBase]) -> str:
        return "\n\n".join(
            "\n".join(
                [
                    f"# Skill: {skill.name}",
                    skill.description,
                    "",
                    skill.instructions,
                    "",
                    cls._build_resource_context(skill),
                    "",
                    (
                        "Available tool: SkillExecutionTool. Use this single "
                        "tool "
                    ),
                    (
                        "to run skill-local argv command arrays when execution "  # noqa: E501
                        "is "
                        "needed."
                    ),
                ]
            ).strip()
            for skill in skills
        )

    @classmethod
    def _build_resource_context(cls, skill: SkillBase) -> str:
        lines = ["## Skill Resources"]
        has_resources = False
        for field_name in ("references", "scripts", "assets"):
            values = list(getattr(skill, field_name, []))
            if not values:
                continue
            has_resources = True
            lines.append(f"- {field_name}: {', '.join(values)}")
        if not has_resources:
            lines.append("- none")
        return "\n".join(lines)

    @classmethod
    def _skill_matches_input(cls, skill: SkillBase, input_text: str) -> bool:
        candidates = [skill.name, skill.description]
        metadata = skill.metadata or {}
        for key in ("tags", "triggers"):
            value = metadata.get(key)
            if isinstance(value, str):
                candidates.append(value)
            elif isinstance(value, Iterable):
                candidates.extend(str(item) for item in value)
        return any(
            candidate and str(candidate).lower() in input_text
            for candidate in candidates
        )

    @staticmethod
    def _input_text(input_data: Union[str, IMessage]) -> str:
        if isinstance(input_data, str):
            return input_data
        return str(getattr(input_data, "content", ""))

    @staticmethod
    def _to_message(input_data: Union[str, IMessage]) -> IMessage:
        if isinstance(input_data, str):
            return HumanMessage(content=input_data)
        if isinstance(input_data, IMessage):
            return input_data
        raise TypeError(
            "Input data must be a string or an instance of Message."
        )

    @staticmethod
    def _normalize_inputs(
        input_data: Optional[
            Union[str, IMessage, Sequence[Union[str, IMessage]]]
        ],
    ) -> List[Union[str, IMessage]]:
        if input_data is None:
            return [""]
        if isinstance(input_data, str) or isinstance(input_data, IMessage):
            return [input_data]
        return list(input_data)
