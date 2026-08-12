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


def test_serialization_proof_compares_python_semantics(pytester):
    """Accept round trips of unordered values regardless of JSON ordering."""
    pytester.makeconftest(
        """
        import json
        from typing import ClassVar, Literal

        from swarmauri_base.ComponentBase import ComponentBase
        from swarmauri_tests_component import ComponentSpec

        @ComponentBase.register_type(ComponentBase, "ReorderedModel")
        class ReorderedModel(ComponentBase):
            type: Literal["ReorderedModel"] = "ReorderedModel"
            values: frozenset[str] = frozenset({"alpha", "beta"})
            _sort_next: ClassVar[bool] = False

            def model_dump_json(self, **kwargs):
                payload = json.loads(super().model_dump_json(**kwargs))
                type(self)._sort_next = not type(self)._sort_next
                return json.dumps(payload, sort_keys=type(self)._sort_next)

        def pytest_swarmauri_component_specs():
            return [
                ComponentSpec(
                    component_class=ReorderedModel,
                    init_kwargs={},
                    expected_resource="ComponentBase",
                    expected_name=None,
                    base_class=ComponentBase,
                )
            ]
        """
    )
    result = pytester.runpytest("-p", "swarmauri_tests_component", "-q")
    result.assert_outcomes(passed=5)


def test_executes_sync_and_async_method_proofs(pytester):
    pytester.makeconftest(
        """
        from typing import Literal

        from swarmauri_base.ComponentBase import ComponentBase
        from swarmauri_tests_component import ComponentSpec, MethodSpec

        @ComponentBase.register_type(ComponentBase, "MethodModel")
        class MethodModel(ComponentBase):
            type: Literal["MethodModel"] = "MethodModel"

            def ping(self): return "pong"
            async def aping(self): return "apong"

        def prove_ping(component):
            assert component.ping() == "pong"

        async def prove_aping(component):
            assert await component.aping() == "apong"

        def pytest_swarmauri_component_specs():
            return [ComponentSpec(
                MethodModel, {}, "ComponentBase", None, ComponentBase,
                method_specs=(
                    MethodSpec("ping", prove_ping),
                    MethodSpec("aping", prove_aping),
                ),
            )]
        """
    )
    result = pytester.runpytest("-p", "swarmauri_tests_component", "-q")
    result.assert_outcomes(passed=7)


def test_rejects_missing_public_method_proof(pytester):
    pytester.makeconftest(
        """
        from typing import Literal
        from swarmauri_base.ComponentBase import ComponentBase
        from swarmauri_tests_component import ComponentSpec

        @ComponentBase.register_type(ComponentBase, "UnprovenModel")
        class UnprovenModel(ComponentBase):
            type: Literal["UnprovenModel"] = "UnprovenModel"
            def unproven(self): return None

        def pytest_swarmauri_component_specs():
            return [ComponentSpec(
                UnprovenModel, {}, "ComponentBase", None, ComponentBase,
                method_specs=(),
            )]
        """
    )
    result = pytester.runpytest("-p", "swarmauri_tests_component", "-q")
    assert result.ret != 0
    assert "missing=['unproven']" in result.stderr.str()


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
