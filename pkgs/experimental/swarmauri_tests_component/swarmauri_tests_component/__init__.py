"""Generate the universal conformance proofs for Swarmauri components."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import DynamicBase

PLUGIN_NAME = __name__.split(".")[0]
PROOFS = (
    "construction",
    "identity",
    "resource",
    "serialization",
    "registration",
)


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
        assert restored.model_dump_json() == serialized
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
        for proof in PROOFS:
            items.append(
                ComponentProofItem.from_parent(
                    session,
                    name=f"{PLUGIN_NAME}:{spec.test_id}:{proof}",
                    spec=spec,
                    proof=proof,
                )
            )


__all__ = ["ComponentSpec", "PROOFS"]
