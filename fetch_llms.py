from pkgs.swarmauri_standard.swarmauri_standard.llms.AnthropicModel import (
    AnthropicModel,
)
from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_KEY = getenv("ANTHROPIC_API_KEY")

model = AnthropicModel(api_key=API_KEY)

print(model.get_allowed_models())
