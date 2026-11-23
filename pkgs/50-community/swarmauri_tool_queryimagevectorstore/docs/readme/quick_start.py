from swarmauri_tool_queryimagevectorstore import QueryImageVectorStoreTool


def query_image_index(*, image_payload, my_image_index, my_vision_embedder):
    """Bind caller-owned resources before executing this integration."""
    tool = QueryImageVectorStoreTool(
        vector_store=my_image_index,
        image_embedder=my_vision_embedder,
    )

    matches = tool(
        image=image_payload,
        top_k=5,
        metadata_filter={"category": "diagram"},
    )
