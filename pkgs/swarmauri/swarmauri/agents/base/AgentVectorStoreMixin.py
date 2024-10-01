from pydantic import BaseModel, ConfigDict
from swarmauri_core.typing import SubclassUnion
from swarmauri_core.agents.IAgentVectorStore import IAgentVectorStore
from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase

class AgentVectorStoreMixin(IAgentVectorStore, BaseModel):
    vector_store: SubclassUnion[VectorStoreBase]
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)