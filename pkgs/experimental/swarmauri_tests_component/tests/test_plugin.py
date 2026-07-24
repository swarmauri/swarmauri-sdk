"""Test generated proofs through pytest's isolated pytester runner."""

import pytest

pytest_plugins = ["pytester"]


@pytest.fixture(autouse=True)
def disable_nested_plugin_autoload(monkeypatch):
    """Keep nested pytest runs isolated from unrelated entry points."""
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")


@pytest.fixture
def component_suite(pytester):
    """Create a registered component and its conformance declaration."""
    pytester.makeconftest(
        """
        from typing import Literal

        from pydantic import Field, SecretStr
        from swarmauri_base.ComponentBase import ComponentBase
        from swarmauri_base.llms.LLMBase import LLMBase
        from swarmauri_tests_component import ComponentSpec

        @ComponentBase.register_type(LLMBase, "ExampleModel")
        class ExampleModel(LLMBase):
            api_key: SecretStr = Field(exclude=True)
            name: str = "example/model"
            type: Literal["ExampleModel"] = "ExampleModel"
            allowed_models: list[str] = Field(default_factory=lambda: ["*"])

            def predict(self, *args, **kwargs): pass
            async def apredict(self, *args, **kwargs): pass
            def stream(self, *args, **kwargs): return iter(())
            async def astream(self, *args, **kwargs): yield ""
            def batch(self, *args, **kwargs): return []
            async def abatch(self, *args, **kwargs): return []

        def pytest_swarmauri_component_specs():
            return [
                ComponentSpec(
                    component_class=ExampleModel,
                    init_kwargs={"api_key": "test-key"},
                    expected_resource="LLM",
                    expected_name="example/model",
                    base_class=LLMBase,
                    round_trip_overrides={"api_key": "test-key"},
                    excluded_fields=("api_key",),
                )
            ]
        """
    )
    return pytester


def test_generates_all_five_proofs(component_suite):
    result = component_suite.runpytest(
        "-p", "swarmauri_tests_component", "-vv"
    )
    result.assert_outcomes(passed=5)
    result.stdout.fnmatch_lines(
        [
            "*swarmauri_tests_component:ExampleModel:construction*",
            "*swarmauri_tests_component:ExampleModel:identity*",
            "*swarmauri_tests_component:ExampleModel:resource*",
            "*swarmauri_tests_component:ExampleModel:serialization*",
            "*swarmauri_tests_component:ExampleModel:registration*",
        ]
    )


@pytest.mark.parametrize(
    ("type_name", "override", "failed_proof"),
    [
        ("BrokenIdentityModel", 'expected_name="wrong",', "identity"),
        ("BrokenResourceModel", 'expected_resource="ToolLLM",', "resource"),
    ],
)
def test_reports_contract_failures(
    pytester, type_name, override, failed_proof
):
    pytester.makeconftest(
        f"""
        from typing import Literal
        from pydantic import Field
        from swarmauri_base.ComponentBase import ComponentBase
        from swarmauri_base.llms.LLMBase import LLMBase
        from swarmauri_tests_component import ComponentSpec

        @ComponentBase.register_type(LLMBase, "{type_name}")
        class {type_name}(LLMBase):
            name: str = "actual"
            type: Literal["{type_name}"] = "{type_name}"
            allowed_models: list[str] = Field(default_factory=lambda: ["*"])

            def predict(self, *args, **kwargs): pass
            async def apredict(self, *args, **kwargs): pass
            def stream(self, *args, **kwargs): return iter(())
            async def astream(self, *args, **kwargs): yield ""
            def batch(self, *args, **kwargs): return []
            async def abatch(self, *args, **kwargs): return []

        def pytest_swarmauri_component_specs():
            values = dict(
                component_class={type_name},
                init_kwargs={{}},
                expected_resource="LLM",
                expected_name="actual",
                base_class=LLMBase,
            )
            values.update(dict({override}))
            return [ComponentSpec(**values)]
        """
    )
    result = pytester.runpytest("-p", "swarmauri_tests_component", "-q")
    result.assert_outcomes(passed=4, failed=1)
    result.stdout.fnmatch_lines([f"*{type_name}:{failed_proof}*"])


def test_rejects_duplicate_specs(pytester):
    pytester.makeconftest(
        """
        from swarmauri_base.llms.LLMBase import LLMBase
        from swarmauri_tests_component import ComponentSpec

        def pytest_swarmauri_component_specs():
            spec = ComponentSpec(LLMBase, {}, "LLM", None, LLMBase)
            return [spec, spec]
        """
    )
    result = pytester.runpytest("-p", "swarmauri_tests_component", "-q")
    assert result.ret != 0
    result.stderr.fnmatch_lines(["*duplicate component spec: LLMBase*"])
