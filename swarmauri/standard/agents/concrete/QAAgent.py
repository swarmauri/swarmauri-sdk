from typing import Any, Optional, Dict
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
from swarmauri.standard.agents.base.AgentBase import AgentBase

class QAAgent(AgentBase):

    def exec(self, 
        input_str: Optional[str] = "",
        llm_kwargs: Optional[Dict] = {} 
        ) -> Any:
        
        llm = self.llm
        messages = [HumanMessage(content=input_str)]
        prediction = llm.predict(messages=messages, **llm_kwargs)
        
        return prediction