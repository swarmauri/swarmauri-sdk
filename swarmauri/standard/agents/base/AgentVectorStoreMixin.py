from pydantic import BaseModel, ConfigDict
from swarmauri.core.agents.IAgentVectorStore import IAgentVectorStore
from swarmauri.core.vector_stores.IVectorStore import IVectorStore

class AgentVectorStoreMixin(IAgentVectorStore, BaseModel):
    vector_store: IVectorStore
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)