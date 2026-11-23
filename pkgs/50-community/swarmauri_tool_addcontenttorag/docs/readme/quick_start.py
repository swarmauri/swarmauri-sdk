from swarmauri_tool_addcontenttorag import AddContentToRAGTool


class InMemoryKnowledgeBase:
    """Any object with add_documents(documents) works."""

    def __init__(self):
        self.documents = []

    def add_documents(self, documents):
        self.documents.extend(documents)


knowledge_base = InMemoryKnowledgeBase()

tool = AddContentToRAGTool()
tool.knowledge_base = knowledge_base

tool(
    content="Reset your password from Settings.",
    metadata={"source": "handbook"},
)
# {"added": 1, "content_length": 34, "metadata": {"source": "handbook"}}

knowledge_base.documents
# [{"content": "Reset your password from Settings.",
#   "metadata": {"source": "handbook"}}]
