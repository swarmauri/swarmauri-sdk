REGISTRY = {
    # Mapping for swarmauri.llms.OpenAIModel
    "swarmauri.llms.OpenAIModel": "httpx"
}

def get_external_module_path(resource_path):
    """
    Get the external module path for a given resource path.
    
    :param resource_path: Full resource path (e.g., "swarmauri.llms.OpenAIModel.OpenAiModel").
    :return: External module path (e.g., "external_repo.OpenAiModel") or None if not found.
    """
    return REGISTRY.get(resource_path)
