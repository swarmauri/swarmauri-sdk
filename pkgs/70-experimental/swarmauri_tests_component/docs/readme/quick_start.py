from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_tests_component import ComponentSpec
from your_package import YourModel


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            component_class=YourModel,
            init_kwargs={"api_key": "test-key", "allowed_models": ["*"]},
            expected_resource="LLM",
            expected_name="provider/model",
            base_class=LLMBase,
            round_trip_overrides={"api_key": "test-key"},
            excluded_fields=("api_key",),
        )
    ]
