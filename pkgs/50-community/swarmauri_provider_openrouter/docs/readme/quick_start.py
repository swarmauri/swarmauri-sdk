from swarmauri_provider_openrouter import (
    OpenRouterProvider,
    OpenRouterProviderPreferences,
)

provider = OpenRouterProvider(
    api_key="...",
    site_url="https://example.com",
    app_name="My application",
)
config = provider.connection_config(
    "chat.completions",
    model="openai/gpt-4o-mini",
)
headers = provider.authorize(config)
routing = OpenRouterProviderPreferences(order=["OpenAI"])
