from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, Sequence, Union

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_base.agents.AgentSystemContextMixin import AgentSystemContextMixin
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.skills.SkillBase import SkillBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.messages.IMessage import IMessage
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
    skill_execution_tool: SubclassUnion[ToolBase] = Field(
        default_factory=SkillExecutionTool
    )
    turn_mode: Literal["single", "multi"] = "multi"
    execution_mode: Literal["sequential", "concurrent"] = "sequential"
    require_skill: bool = False
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["SkillAgent"] = "SkillAgent"

    def exec(
        self,
        input_str: Optional[Union[str, IMessage, Sequence[Union[str, IMessage]]]] = "",
        llm_kwargs: Optional[Dict] = None,
        skill_names: Optional[Sequence[str]] = None,
    ) -> Any:
        inputs = self._normalize_inputs(input_str)
        if len(inputs) == 1:
            return self._exec_one(
                inputs[0], llm_kwargs=llm_kwargs, skill_names=skill_names
            )
        return [
            self._exec_one(item, llm_kwargs=llm_kwargs, skill_names=skill_names)
            for item in inputs
        ]

    async def aexec(
        self,
        input_str: Optional[Union[str, IMessage, Sequence[Union[str, IMessage]]]] = "",
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

    def select_skills(
        self,
        input_data: Union[str, IMessage],
        skill_names: Optional[Sequence[str]] = None,
    ) -> List[SkillBase]:
        if skill_names:
            selected = [
                skill for skill in self.skills if skill.name in set(skill_names)
            ]
            missing = sorted(set(skill_names) - {skill.name for skill in selected})
            if missing:
                raise ValueError(f"Unknown skill name(s): {', '.join(missing)}")
            return selected

        if len(self.skills) == 1:
            return list(self.skills)

        input_text = self._input_text(input_data).lower()
        selected = [
            skill
            for skill in self.skills
            if self._skill_matches_input(skill, input_text)
        ]
        if not selected and self.require_skill:
            raise ValueError("No matching skill found for input")
        return selected

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
            **self._llm_kwargs(selected_skills, llm_kwargs, method_name="apredict"),
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

        selected_skills = self.select_skills(input_data, skill_names=skill_names)
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
            kwargs.setdefault("toolkit", self.get_skill_toolkit(selected_skills))
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
                    "Available tool: SkillExecutionTool. Use this single tool "
                    "to run skill-local argv command arrays when execution is needed.",
                ]
            ).strip()
            for skill in skills
        )

    @classmethod
    def _build_resource_context(cls, skill: SkillBase) -> str:
        lines = ["## Skill Resources"]
        has_resources = False
        for field_name in SkillBase._RESOURCE_FIELDS:
            values = list(getattr(skill, field_name))
            if not values:
                continue
            has_resources = True
            lines.append(f"- {field_name}: {', '.join(values)}")
            if field_name in {"agents", "references"}:
                for value in values:
                    content = cls._read_resource_content(skill, value)
                    if content:
                        lines.append(f"\n### {field_name}/{value}\n{content}")
        if not has_resources:
            lines.append("- none")
        return "\n".join(lines)

    @staticmethod
    def _read_resource_content(skill: SkillBase, resource_path: str) -> str:
        root_path = getattr(skill, "root_path", None)
        if not root_path:
            return ""
        root = Path(root_path).expanduser().resolve()
        path = (root / resource_path).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            return ""
        if path.suffix.lower() not in {".md", ".yaml", ".yml"} or not path.is_file():
            return ""
        return path.read_text(encoding="utf-8").strip()

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
        raise TypeError("Input data must be a string or an instance of Message.")

    @staticmethod
    def _normalize_inputs(
        input_data: Optional[Union[str, IMessage, Sequence[Union[str, IMessage]]]],
    ) -> List[Union[str, IMessage]]:
        if input_data is None:
            return [""]
        if isinstance(input_data, str) or isinstance(input_data, IMessage):
            return [input_data]
        return list(input_data)
