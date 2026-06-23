from __future__ import annotations

import inspect
from typing import Any, Dict, List, Literal, Optional, Sequence, Union

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.skills.SkillBase import SkillBase
from swarmauri_core.messages.IMessage import IMessage


@ComponentBase.register_type(AgentBase, "SkillAgent")
class SkillAgent(AgentBase):
    llm: Any = None
    agent: SubclassUnion[AgentBase]
    skills: List[SubclassUnion[SkillBase]] = Field(default_factory=list)
    turn_mode: Literal["single", "multi"] = "multi"
    execution_mode: Literal["sequential", "concurrent"] = "sequential"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["SkillAgent"] = "SkillAgent"

    def exec(
        self,
        input_str: Optional[Union[str, IMessage, Sequence[Union[str, IMessage]]]] = "",
        llm_kwargs: Optional[Dict] = None,
    ) -> Any:
        inputs = self._normalize_inputs(input_str)
        if len(inputs) == 1:
            return self._exec_one(inputs[0], llm_kwargs=llm_kwargs)
        if self.execution_mode == "concurrent":
            return self.agent.batch(
                [self._apply_skill_context(item) for item in inputs],
                llm_kwargs=llm_kwargs,
            )
        return [self._exec_one(item, llm_kwargs=llm_kwargs) for item in inputs]

    async def aexec(
        self,
        input_str: Optional[Union[str, IMessage, Sequence[Union[str, IMessage]]]] = "",
        llm_kwargs: Optional[Dict] = None,
    ) -> Any:
        inputs = self._normalize_inputs(input_str)
        if len(inputs) == 1:
            return await self._aexec_one(inputs[0], llm_kwargs=llm_kwargs)
        if self.execution_mode == "concurrent":
            return await self.agent.abatch(
                [self._apply_skill_context(item) for item in inputs],
                llm_kwargs=llm_kwargs,
            )
        results = []
        for item in inputs:
            results.append(await self._aexec_one(item, llm_kwargs=llm_kwargs))
        return results

    def _exec_one(
        self, input_data: Union[str, IMessage], llm_kwargs: Optional[Dict] = None
    ) -> Any:
        payload = self._apply_skill_context(input_data)
        kwargs = {"llm_kwargs": llm_kwargs}
        if self._accepts_multiturn(self.agent.exec):
            kwargs["multiturn"] = self.turn_mode == "multi"
        return self.agent.exec(payload, **kwargs)

    async def _aexec_one(
        self, input_data: Union[str, IMessage], llm_kwargs: Optional[Dict] = None
    ) -> Any:
        payload = self._apply_skill_context(input_data)
        kwargs = {"llm_kwargs": llm_kwargs}
        if self._accepts_multiturn(self.agent.aexec):
            kwargs["multiturn"] = self.turn_mode == "multi"
        return await self.agent.aexec(payload, **kwargs)

    def _apply_skill_context(
        self, input_data: Union[str, IMessage]
    ) -> Union[str, IMessage]:
        if not isinstance(input_data, str) or not self.skills:
            return input_data
        context = "\n\n".join(
            f"# Skill: {skill.name}\n{skill.description}\n\n{skill.instructions}"
            for skill in self.skills
        )
        return f"{context}\n\n# User Input\n{input_data}"

    @staticmethod
    def _accepts_multiturn(method: Any) -> bool:
        return "multiturn" in inspect.signature(method).parameters

    @staticmethod
    def _normalize_inputs(
        input_data: Optional[Union[str, IMessage, Sequence[Union[str, IMessage]]]],
    ) -> List[Union[str, IMessage]]:
        if input_data is None:
            return [""]
        if isinstance(input_data, str) or isinstance(input_data, IMessage):
            return [input_data]
        return list(input_data)
