from typing import Union
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage
from swarmauri.core.agents.IAgentSystemContext import IAgentSystemContext


class SystemContextAgentBase(IAgentSystemContext):
    def __init__(self, system_context: Union[SystemMessage, str]):
        if isinstance(system_context, SystemMessage):
            self._system_context
        else:    
            self._system_context = SystemMessage(system_context)

    @property
    def system_context(self) -> SystemMessage:
        return self._system_context

    @system_context.setter
    def system_context(self, value: Union[SystemMessage, str]) -> None:
        if isinstance(value, SystemMessage):
            self._system_context
        else:    
            self._system_context = SystemMessage(value)