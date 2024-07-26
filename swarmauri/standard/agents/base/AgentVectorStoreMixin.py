from pydantic import BaseModel, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.agents.IAgentVectorStore import IAgentVectorStore
from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase

class AgentVectorStoreMixin(IAgentVectorStore, BaseModel):
    vector_store: SubclassUnion[VectorStoreBase]
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)