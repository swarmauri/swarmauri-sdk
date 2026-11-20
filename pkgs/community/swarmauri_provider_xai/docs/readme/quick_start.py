from swarmauri_provider_xai import XAIProvider

provider = XAIProvider(api_key="...")
config = provider.connection_config("chat.completions", model="grok-4.3")
headers = provider.authorize(config)
