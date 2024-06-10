from swarmauri.standard.messages.base.MessageBase import MessageBase


class FunctionMessage(MessageBase):
    content: str
    name: str
    tool_call_id: str
    _role: str ='tool'

    @property
    def role(self) -> str:
        return self._role