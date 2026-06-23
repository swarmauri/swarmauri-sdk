from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterable, List, Literal, Optional, Sequence, Union

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.agents.AgentConversationMixin import AgentConversationMixin
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.skills.SkillBase import SkillBase
from swarmauri_core.messages.IMessage import IMessage
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage


@ComponentBase.register_type(AgentBase, "SkillAgent")
class SkillAgent(AgentConversationMixin, AgentBase):
    llm: SubclassUnion[LLMBase]
    conversation: SubclassUnion[ConversationBase]
    skills: List[SubclassUnion[SkillBase]] = Field(default_factory=list)
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
        conversation = self._prepare_conversation(input_data, skill_names=skill_names)
        result = self.llm.predict(conversation=conversation, **(llm_kwargs or {}))
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
        conversation = self._prepare_conversation(input_data, skill_names=skill_names)
        result = await self.llm.apredict(
            conversation=conversation, **(llm_kwargs or {})
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
    ) -> ConversationBase:
        conversation = self.conversation
        if self.turn_mode == "single":
            conversation = self.conversation.model_copy(deep=True)
            conversation.clear_history()

        selected_skills = self.select_skills(input_data, skill_names=skill_names)
        skill_context = self._build_skill_context(selected_skills)
        if skill_context:
            conversation.add_message(SystemMessage(content=skill_context))
        conversation.add_message(self._to_message(input_data))
        return conversation

    @staticmethod
    def _build_skill_context(skills: Iterable[SkillBase]) -> str:
        return "\n\n".join(
            f"# Skill: {skill.name}\n{skill.description}\n\n{skill.instructions}"
            for skill in skills
        )

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
