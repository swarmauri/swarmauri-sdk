from typing import List
from pydantic import BaseModel, ConfigDict, Field
from swarmauri_core.agents.IAgentRetrieve import IAgentRetrieve
from swarmauri_core.documents.IDocument import IDocument


class AgentRetrieveMixin(IAgentRetrieve, BaseModel):
    last_retrieved: List[IDocument] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
