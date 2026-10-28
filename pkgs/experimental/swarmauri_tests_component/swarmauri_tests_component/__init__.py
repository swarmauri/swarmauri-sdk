"""Generate the universal conformance proofs for Swarmauri components."""

from __future__ import annotations

import asyncio
import inspect
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import DynamicBase

PLUGIN_NAME = __name__.split(".")[0]
__version__ = version(PLUGIN_NAME)
PROOFS = (
    "construction",
    "identity",
    "resource",
    "serialization",
    "registration",
)


@dataclass(frozen=True)
class MethodSpec:
    """Executable behavioral proof for one public component method."""

    method_name: str
    exercise: Callable[[ComponentBase], Any]
    case_name: str = "behavior"

    @property
    def test_id(self) -> str:
        return f"{self.method_name}:{self.case_name}"


@dataclass(frozen=True)
class ComponentSpec:
    """Describe one concrete component and its expected universal contract.

    Parameters
    ----------
    component_class:
        Concrete ``ComponentBase`` subclass under test.
    init_kwargs:
        Deterministic constructor arguments. Test credentials are appropriate;
        production secrets must never be placed here.
    expected_resource:
        Resource-family discriminator inherited from the component's base.
    expected_name:
        Public component/model name expected after construction.
    base_class:
        Immediate Swarmauri family base used for inheritance and registration.
    expected_type:
        Concrete type discriminator. Defaults to the class name.
    round_trip_overrides:
        Values intentionally excluded from serialization, such as API keys,
        which must be supplied again when reconstructing the component.
    excluded_fields:
        Sensitive fields that must not appear in serialized output.
    """

    component_class: type[ComponentBase]
    init_kwargs: Mapping[str, Any]
    expected_resource: str
    expected_name: str | None
    base_class: type[ComponentBase]
    expected_type: str | None = None
    round_trip_overrides: Mapping[str, Any] = field(default_factory=dict)
    excluded_fields: Sequence[str] = ()
    method_specs: Sequence[MethodSpec] | None = None

    @property
    def type_name(self) -> str:
        """Return the expected discriminator for the concrete component."""
        return self.expected_type or self.component_class.__name__

    @property
    def test_id(self) -> str:
        """Return a stable pytest identifier for generated proof items."""
        return self.type_name

    def create(self) -> ComponentBase:
        """Construct a fresh component instance for an isolated proof."""
        return self.component_class(**dict(self.init_kwargs))


def live_session_method_specs(
    create_exercise: Callable[[ComponentBase], Any],
) -> tuple[MethodSpec, ...]:
    """Return exhaustive behavioral proofs for a concrete live session."""

    def prove_mark_open(session: ComponentBase) -> None:
        session.mark_open()
        assert session.state == "open"

    async def prove_emit(session: ComponentBase) -> None:
        event = object()
        await session.emit(event)
        assert await session._events.get() is event

    async def prove_finish(session: ComponentBase) -> None:
        await session.finish()
        assert session.state == "closed"
        assert session._closed_event.is_set()

    async def prove_fail(session: ComponentBase) -> None:
        error = RuntimeError("session failed")
        await session.fail(error)
        assert session.state == "failed"
        assert session.terminal_error is error

    def prove_sync_only_error(method_name: str):
        def exercise(session: ComponentBase) -> None:
            with pytest.raises(RuntimeError, match="synchronous live APIs"):
                getattr(session, method_name)(
                    None
                ) if method_name == "send" else getattr(session, method_name)()

        return exercise

    def prove_stream(session: ComponentBase) -> None:
        with pytest.raises(RuntimeError, match="synchronous live APIs"):
            next(session.stream())

    async def prove_asend(session: ComponentBase) -> None:
        implementation = AsyncMock()
        object.__setattr__(session, "_asend_impl", implementation)
        session.mark_open()
        value = object()
        await session.asend(value)
        implementation.assert_awaited_once_with(value)

    async def prove_astream(session: ComponentBase) -> None:
        event = object()
        await session.emit(event)
        await session.finish()
        assert [item async for item in session.astream()] == [event]

    async def prove_await_closed(session: ComponentBase) -> None:
        await session.finish()
        await session.await_closed()

    async def prove_aclose(session: ComponentBase) -> None:
        implementation = AsyncMock()
        object.__setattr__(session, "_aclose_impl", implementation)
        session.mark_open()
        await session.aclose()
        implementation.assert_awaited_once_with()
        assert session.state == "closed"

    return (
        MethodSpec("create", create_exercise),
        MethodSpec("mark_open", prove_mark_open),
        MethodSpec("emit", prove_emit),
        MethodSpec("finish", prove_finish),
        MethodSpec("fail", prove_fail),
        MethodSpec("send", prove_sync_only_error("send")),
        MethodSpec("asend", prove_asend),
        MethodSpec("stream", prove_stream),
        MethodSpec("astream", prove_astream),
        MethodSpec("wait_closed", prove_sync_only_error("wait_closed")),
        MethodSpec("await_closed", prove_await_closed),
        MethodSpec("close", prove_sync_only_error("close")),
        MethodSpec("aclose", prove_aclose),
    )


def model_catalog_method_specs() -> tuple[MethodSpec, ...]:
    """Return exhaustive behavioral proofs for a concrete model catalog."""

    def prove_list_models(catalog: ComponentBase) -> None:
        assert list(catalog.list_models()) == list(catalog.models.values())

    def prove_get_model(catalog: ComponentBase) -> None:
        if catalog.models:
            name, expected = next(iter(catalog.models.items()))
            assert catalog.get_model(name) == expected
        assert catalog.get_model("missing-model") is None

    def prove_refresh(catalog: ComponentBase) -> None:
        assert list(catalog.refresh()) == list(catalog.models.values())
        assert catalog.refreshed_at is not None

    async def prove_arefresh(catalog: ComponentBase) -> None:
        assert list(await catalog.arefresh()) == list(catalog.models.values())
        assert catalog.refreshed_at is not None

    def prove_replace(catalog: ComponentBase) -> None:
        model = SimpleNamespace(name="replacement")
        catalog.replace([model])
        assert catalog.get_model("replacement") is model
        assert catalog.refreshed_at is not None

    return (
        MethodSpec("list_models", prove_list_models),
        MethodSpec("get_model", prove_get_model),
        MethodSpec("refresh", prove_refresh),
        MethodSpec("arefresh", prove_arefresh),
        MethodSpec("replace", prove_replace),
    )


class SwarmauriComponentHookSpecs:
    """Declare extension hooks consumed by the conformance plugin."""

    @pytest.hookspec
    def pytest_swarmauri_component_specs(self) -> Sequence[ComponentSpec]:
        """Return component specifications owned by the current test suite."""


def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    """Register the component-specification hook with pytest."""
    pluginmanager.add_hookspecs(SwarmauriComponentHookSpecs)


def pytest_configure(config: pytest.Config) -> None:
    """Register the marker used by generated component proof items."""
    config.addinivalue_line(
        "markers",
        "component: generated Swarmauri component conformance proofs",
    )


class ComponentProofItem(pytest.Item):
    """Execute one named universal proof for one component specification."""

    def __init__(
        self,
        name: str,
        parent: pytest.Collector,
        *,
        spec: ComponentSpec,
        proof: str,
    ) -> None:
        super().__init__(name, parent)
        self.spec = spec
        self.proof = proof
        self.add_marker("component")

    def runtest(self) -> None:
        """Dispatch the generated item to its contract proof."""
        getattr(self, f"_prove_{self.proof}")()

    def _prove_construction(self) -> None:
        component = self.spec.create()
        assert isinstance(component, ComponentBase)
        assert isinstance(component, self.spec.base_class)

    def _prove_identity(self) -> None:
        component = self.spec.create()
        assert component.type == self.spec.type_name
        assert component.name == self.spec.expected_name

    def _prove_resource(self) -> None:
        component = self.spec.create()
        assert component.resource == self.spec.expected_resource

    def _prove_serialization(self) -> None:
        component = self.spec.create()
        serialized = component.model_dump_json()
        payload = json.loads(serialized)
        for field_name in self.spec.excluded_fields:
            assert field_name not in payload
        restored = self.spec.component_class.model_validate(
            {**payload, **dict(self.spec.round_trip_overrides)}
        )
        assert restored.model_dump() == component.model_dump()
        assert restored.id == component.id
        assert restored.type == component.type
        assert restored.name == component.name
        assert restored.resource == component.resource

    def _prove_registration(self) -> None:
        entry = DynamicBase._registry.get(self.spec.base_class.__name__)
        assert entry is not None
        assert (
            entry["subtypes"].get(self.spec.type_name)
            is self.spec.component_class
        )

    def reportinfo(self) -> tuple[Path, None, str]:
        """Describe the generated proof in pytest's standard reports."""
        return (
            Path.cwd(),
            None,
            f"component {self.proof} proof for {self.spec.test_id}",
        )


class ComponentMethodProofItem(pytest.Item):
    """Execute one declared public-method behavior proof."""

    def __init__(
        self,
        name: str,
        parent: pytest.Collector,
        *,
        spec: ComponentSpec,
        method_spec: MethodSpec,
    ) -> None:
        super().__init__(name, parent)
        self.spec = spec
        self.method_spec = method_spec
        self.add_marker("component")

    def runtest(self) -> None:
        component = self.spec.create()
        result = self.method_spec.exercise(component)
        if inspect.isawaitable(result):
            asyncio.run(result)

    def reportinfo(self) -> tuple[Path, None, str]:
        return (
            Path.cwd(),
            None,
            "component method proof "
            f"{self.spec.test_id}.{self.method_spec.test_id}",
        )


def _public_component_methods(spec: ComponentSpec) -> set[str]:
    """Find methods declared between a component and its family base."""
    methods: set[str] = set()
    framework_methods = set(BaseModel.__dict__)
    for cls in spec.component_class.__mro__:
        for name, value in cls.__dict__.items():
            if name.startswith("_") or name in framework_methods:
                continue
            if isinstance(value, (staticmethod, classmethod)):
                value = value.__func__
            if callable(value):
                methods.add(name)
        if cls is spec.base_class:
            break
    return methods


def _validate_method_specs(spec: ComponentSpec) -> None:
    if spec.method_specs is None:
        return
    required = _public_component_methods(spec)
    declared = {method.method_name for method in spec.method_specs}
    missing = required - declared
    unknown = declared - required
    if missing or unknown:
        raise pytest.UsageError(
            f"invalid method proofs for {spec.test_id}: "
            f"missing={sorted(missing)}, unknown={sorted(unknown)}"
        )


def _component_specs(config: pytest.Config) -> list[ComponentSpec]:
    """Collect component specifications from all hook providers."""
    specs: list[ComponentSpec] = []
    for result in config.hook.pytest_swarmauri_component_specs():
        if result:
            specs.extend(result)
    seen: set[str] = set()
    for spec in specs:
        if not isinstance(spec, ComponentSpec):
            raise pytest.UsageError(
                "pytest_swarmauri_component_specs must return "
                "ComponentSpec values"
            )
        if spec.test_id in seen:
            raise pytest.UsageError(
                f"duplicate component spec: {spec.test_id}"
            )
        seen.add(spec.test_id)
    return specs


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Append five reported proofs for every declared component."""
    if getattr(config, "_swarmauri_component_items_added", False):
        return
    config._swarmauri_component_items_added = True
    for spec in _component_specs(config):
        _validate_method_specs(spec)
        for proof in PROOFS:
            items.append(
                ComponentProofItem.from_parent(
                    session,
                    name=f"{PLUGIN_NAME}:{spec.test_id}:{proof}",
                    spec=spec,
                    proof=proof,
                )
            )
        for method_spec in spec.method_specs or ():
            items.append(
                ComponentMethodProofItem.from_parent(
                    session,
                    name=(
                        f"{PLUGIN_NAME}:{spec.test_id}:method:"
                        f"{method_spec.test_id}"
                    ),
                    spec=spec,
                    method_spec=method_spec,
                )
            )


__all__ = [
    "ComponentSpec",
    "MethodSpec",
    "PROOFS",
    "__version__",
    "live_session_method_specs",
    "model_catalog_method_specs",
]
