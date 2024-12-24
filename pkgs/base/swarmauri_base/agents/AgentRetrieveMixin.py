from abc import ABC
from typing import List
from pydantic import BaseModel, ConfigDict, field_validator, Field
from swarmauri_standard.documents.Document import Document
from swarmauri_core.agents.IAgentRetrieve import IAgentRetrieve

class AgentRetrieveMixin(IAgentRetrieve, BaseModel):
    last_retrieved: List[Document] = Field(default_factory=list)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

