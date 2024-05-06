from typing import Any, Optional

from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation

from swarmauri.standard.agents.base.AgentBase import AgentBase

class QAAgent(AgentBase):
    def __init__(self, model: IModel):
        AgentBase.__init__(self, model=model)

    def exec(self, input_str: Optional[str] = None) -> Any:
        model = self.model
        prediction = model.predict(input_str)
        
        return prediction