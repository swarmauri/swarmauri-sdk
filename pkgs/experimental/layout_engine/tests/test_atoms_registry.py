from __future__ import annotations

from layout_engine.atoms.default import AtomRegistry
from layout_engine.atoms.spec import AtomSpec


def test_atom_registry_override_merges_defaults_and_registry() -> None:
    registry = AtomRegistry()
    base = AtomSpec(
        role="swarmakit:vue:button",
        module="@swarmakit/vue",
        export="Button",
        version="0.0.22",
        defaults={"size": "md"},
        framework="vue",
        package="@swarmakit/vue",
        registry={"name": "swarmakit", "version": "0.0.22"},
        tokens={"spacing": "m"},
    )
    registry.register(base)

    updated = registry.override(
        "swarmakit:vue:button",
        defaults={"tone": "primary"},
        registry={"version": "0.0.23"},
        tokens={"spacing": "l"},
    )

    assert updated.defaults == {"size": "md", "tone": "primary"}
    assert updated.registry["version"] == "0.0.23"
    assert updated.registry["name"] == "swarmakit"
    assert updated.tokens["spacing"] == "l"
