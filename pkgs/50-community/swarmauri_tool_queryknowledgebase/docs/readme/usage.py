from swarmauri_tool_queryknowledgebase import QueryKnowledgeBaseTool


def query_documents(*, my_document_store):
    """Bind caller-owned resources before executing this integration."""
    tool = QueryKnowledgeBaseTool(knowledge_base=my_document_store)
    results = tool(
        "How are API keys rotated?",
        top_k=3,
        metadata_filter={"product": "sdk"},
    )

    for result in results:
        print(result["rank"], result["content"], result["metadata"])
