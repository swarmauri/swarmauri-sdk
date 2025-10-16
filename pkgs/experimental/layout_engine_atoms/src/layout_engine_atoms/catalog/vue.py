from __future__ import annotations

from typing import Iterable, Mapping

from layout_engine import AtomRegistry, AtomSpec

from ..spec import AtomPreset
from ..shortcuts import build_registry as build_registry_from_presets


DEFAULT_PRESETS: dict[str, AtomPreset] = {
    "ui:text:body": AtomPreset(
        role="ui:text:body",
        module="@swarmauri/atoms/Typography",
        export="BodyText",
        defaults={"variant": "body", "weight": "regular"},
        family="typography",
        description="Paragraph copy for long-form content blocks.",
    ),
    "ui:text:caption": AtomPreset(
        role="ui:text:caption",
        module="@swarmauri/atoms/Typography",
        export="CaptionText",
        defaults={"variant": "caption", "weight": "medium"},
        family="typography",
        description="Caption text used for footnotes or metadata labels.",
    ),
    "ui:button:primary": AtomPreset(
        role="ui:button:primary",
        module="@swarmauri/atoms/Button",
        export="PrimaryButton",
        defaults={"kind": "primary", "size": "md"},
        family="actions",
        description="Primary call-to-action button with accent styling.",
    ),
    "ui:button:secondary": AtomPreset(
        role="ui:button:secondary",
        module="@swarmauri/atoms/Button",
        export="SecondaryButton",
        defaults={"kind": "secondary", "size": "md"},
        family="actions",
        description="Secondary button used for neutral or cancel actions.",
    ),
    "ui:badge:status": AtomPreset(
        role="ui:badge:status",
        module="@swarmauri/atoms/Badge",
        export="StatusBadge",
        defaults={"variant": "info"},
        family="status",
        description="Compact status badge for metadata and list items.",
    ),
    "viz:timeseries:line": AtomPreset(
        role="viz:timeseries:line",
        module="@swarmauri/atoms/charts/Timeseries",
        export="LineChart",
        defaults={"legend": True, "curve": "smooth"},
        family="visualization",
        description="Responsive line chart for time-series data.",
    ),
    "viz:bar:horizontal": AtomPreset(
        role="viz:bar:horizontal",
        module="@swarmauri/atoms/charts/Bar",
        export="HorizontalBar",
        defaults={"legend": False, "stacked": False},
        family="visualization",
        description="Horizontal bar chart for categorical comparisons.",
    ),
    "viz:metric:kpi": AtomPreset(
        role="viz:metric:kpi",
        module="@swarmauri/atoms/Metrics",
        export="KpiCard",
        defaults={"format": "compact", "sparkline": False},
        family="metrics",
        description="Single KPI tile showing value, delta, and trend.",
    ),
    "viz:table:basic": AtomPreset(
        role="viz:table:basic",
        module="@swarmauri/atoms/Table",
        export="DataTable",
        defaults={"striped": True, "dense": False},
        family="data",
        description="Paginated data table with sortable headers.",
    ),
    "layout:card": AtomPreset(
        role="layout:card",
        module="@swarmauri/atoms/Layout",
        export="SurfaceCard",
        defaults={"padding": "lg", "elevation": 2},
        family="layout",
        description="Surface container used to group related atoms.",
    ),
    "layout:grid:two-up": AtomPreset(
        role="layout:grid:two-up",
        module="@swarmauri/atoms/Layout",
        export="TwoUpGrid",
        defaults={"gap": "lg"},
        family="layout",
        description="Two-column grid wrapper for responsive sections.",
    ),
    "input:select": AtomPreset(
        role="input:select",
        module="@swarmauri/atoms/Inputs",
        export="SelectField",
        defaults={"filterable": True, "clearable": True},
        family="inputs",
        description="Dropdown input with optional search and clear actions.",
    ),
    "input:date-range": AtomPreset(
        role="input:date-range",
        module="@swarmauri/atoms/Inputs",
        export="DateRangePicker",
        defaults={"presets": ["7d", "30d", "90d"]},
        family="inputs",
        description="Date range picker with quick preset shortcuts.",
    ),
}

DEFAULT_ATOMS: dict[str, AtomSpec] = {
    role: preset.to_spec() for role, preset in DEFAULT_PRESETS.items()
}

PRESET_VERSION = "0.1.0"


def build_default_registry() -> AtomRegistry:
    """Return an :class:`AtomRegistry` populated with the default presets."""
    return build_registry_from_presets(DEFAULT_PRESETS.values())


def build_registry(
    presets: Iterable[AtomPreset] | Mapping[str, AtomPreset] | None = None,
) -> AtomRegistry:
    """Create an :class:`AtomRegistry` populated with the provided presets."""
    if presets is None:
        presets = DEFAULT_PRESETS.values()
    return build_registry_from_presets(presets)
