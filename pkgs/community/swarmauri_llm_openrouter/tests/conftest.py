"""Declare OpenRouter components for universal conformance proofs."""

from swarmauri_base.image_gens.ImageGenBase import ImageGenBase
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_base.tool_llms.ToolLLMBase import ToolLLMBase
from swarmauri_base.vlms.VLMBase import VLMBase
from swarmauri_tests_component import ComponentSpec

from swarmauri_llm_openrouter import (
    OpenRouterImgGenModel,
    OpenRouterModel,
    OpenRouterToolModel,
    OpenRouterVLM,
)

_COMMON = {
    "api_key": "test-key",
    "allowed_models": ["*"],
}
_ROUND_TRIP = {"api_key": "test-key"}
_EXCLUDED = ("api_key",)


def pytest_swarmauri_component_specs():
    """Return every public OpenRouter component and its expected contract."""
    return [
        ComponentSpec(
            component_class=OpenRouterModel,
            init_kwargs=_COMMON,
            expected_resource="LLM",
            expected_name="openrouter/auto",
            base_class=LLMBase,
            round_trip_overrides=_ROUND_TRIP,
            excluded_fields=_EXCLUDED,
        ),
        ComponentSpec(
            component_class=OpenRouterToolModel,
            init_kwargs=_COMMON,
            expected_resource="ToolLLM",
            expected_name="openrouter/auto",
            base_class=ToolLLMBase,
            round_trip_overrides=_ROUND_TRIP,
            excluded_fields=_EXCLUDED,
        ),
        ComponentSpec(
            component_class=OpenRouterVLM,
            init_kwargs=_COMMON,
            expected_resource="VLM",
            expected_name="openrouter/auto",
            base_class=VLMBase,
            round_trip_overrides=_ROUND_TRIP,
            excluded_fields=_EXCLUDED,
        ),
        ComponentSpec(
            component_class=OpenRouterImgGenModel,
            init_kwargs=_COMMON,
            expected_resource="ImageGen",
            expected_name="openai/gpt-image-1",
            base_class=ImageGenBase,
            round_trip_overrides=_ROUND_TRIP,
            excluded_fields=_EXCLUDED,
        ),
    ]
