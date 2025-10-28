from __future__ import annotations

from typing import Literal

from layout_engine import AtomSpec

from .base import AtomProps, SwarmaAtom


class VueButtonProps(AtomProps):
    """Props supported by the SwarmaKit Vue Button component."""

    type: Literal["primary", "secondary"] = "primary"
    disabled: bool = False


class SvelteButtonProps(AtomProps):
    """Props supported by the SwarmaKit Svelte Button component."""

    label: str = "Click me"
    type: Literal["primary", "secondary"] = "primary"
    disabled: bool = False
    ariaLabel: str | None = None
    onClick: str | None = None


class ReactButtonProps(AtomProps):
    """Props supported by the SwarmaKit React Button component."""

    label: str = "Click me"
    primary: bool = False
    size: Literal["small", "medium", "large"] = "medium"
    backgroundColor: str | None = None
    onClick: str | None = None


VUE_BUTTON = SwarmaAtom(
    spec=AtomSpec(
        role="ui:button:primary:vue",
        module="@swarmakit/vue",
        export="Button",
        version="0.0.22",
        defaults={"type": "primary", "disabled": False},
    ),
    props_schema=VueButtonProps,
)

SVELTE_BUTTON = SwarmaAtom(
    spec=AtomSpec(
        role="ui:button:primary:svelte",
        module="@swarmakit/svelte",
        export="Button",
        version="0.0.22",
        defaults={
            "label": "Click me",
            "type": "primary",
            "disabled": False,
        },
    ),
    props_schema=SvelteButtonProps,
)

REACT_BUTTON = SwarmaAtom(
    spec=AtomSpec(
        role="ui:button:primary:react",
        module="@swarmakit/react",
        export="Button",
        version="0.0.22",
        defaults={
            "label": "Click me",
            "primary": True,
            "size": "medium",
        },
    ),
    props_schema=ReactButtonProps,
)


__all__ = [
    "VueButtonProps",
    "SvelteButtonProps",
    "ReactButtonProps",
    "VUE_BUTTON",
    "SVELTE_BUTTON",
    "REACT_BUTTON",
]
