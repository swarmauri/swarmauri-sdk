from __future__ import annotations

import re
from typing import Iterable, Mapping

from layout_engine import AtomRegistry, AtomSpec

from ..spec import AtomPreset
from ..swarma import AtomProps, SwarmaAtomCatalog

FRAMEWORK = "svelte"
SWARMAKIT_MODULE = "@swarmakit/svelte"
SWARMAKIT_VERSION = "0.0.22"
PRESET_VERSION = SWARMAKIT_VERSION

_COMPONENT_EXPORTS: tuple[str, ...] = (
    "CheckList",
    "Accordion",
    "ActionableList",
    "ActivityIndicators",
    "AudioPlayer",
    "AudioPlayerAdvanced",
    "AudioWaveformDisplay",
    "Badge",
    "BadgeWithCounts",
    "BatteryLevelIndicator",
    "Button",
    "Captcha",
    "CardbasedList",
    "Carousel",
    "Checkbox",
    "CollapsibleMenuList",
    "ColorPicker",
    "ContextualList",
    "CountdownTimer",
    "DataGrid",
    "DateAndTimePicker",
    "DatePicker",
    "ThreeSixtyDegreeImageViewer",
    "DragAndDropFileArea",
    "EmbeddedMediaIframe",
    "ExpandableList",
    "FavoritesList",
    "FileInputWithPreview",
    "FileUpload",
    "FilterableList",
    "GroupedList",
    "IconButton",
    "ImageSlider",
    "InteractivePollResults",
    "LoadingBarsWithSteps",
    "LoadingSpinner",
    "LoadmorebuttoninList",
    "MultiselectList",
    "NotificationBellIcon",
    "NumberedList",
    "NumberInputWithIncrement",
    "Pagination",
    "PasswordConfirmationField",
    "PinnedList",
    "ProgressBar",
    "ProgressCircle",
    "RadioButton",
    "RangeSlider",
    "RatingStars",
    "ScrollableList",
    "SearchBar",
    "SearchInputWithFilterOptions",
    "SelectableListWithItemDetails",
    "SignalStrengthIndicator",
    "Slider",
    "SortableList",
    "SortableTable",
    "StatusDots",
    "Stepper",
    "SystemAlertGlobalNotificationBar",
    "Tabs",
    "TaskCompletionCheckList",
    "Textarea",
    "TimelineList",
    "Toast",
    "ToggleSwitch",
    "TreeviewList",
    "Upload",
    "ValidationMessages",
    "VirtualizedList",
    "VisualCueForAccessibilityFocusIndicator",
)


def _slugify(name: str) -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    text = re.sub(r"([A-Z])([A-Z][a-z])", r"\1-\2", text)
    return text.replace("_", "-").lower()


def _make_preset(name: str) -> AtomPreset:
    role = f"swarmakit:svelte:{_slugify(name)}"
    return AtomPreset(
        role=role,
        module=SWARMAKIT_MODULE,
        export=name,
        version=SWARMAKIT_VERSION,
        defaults={},
        framework=FRAMEWORK,
        package=SWARMAKIT_MODULE,
        family="swarmakit",
        registry={
            "name": "swarmakit",
            "framework": FRAMEWORK,
            "package": SWARMAKIT_MODULE,
            "version": SWARMAKIT_VERSION,
        },
    )


_DEFAULT_PRESETS = tuple(_make_preset(name) for name in _COMPONENT_EXPORTS)

DEFAULT_PRESETS: dict[str, AtomPreset] = {
    preset.role: preset for preset in _DEFAULT_PRESETS
}

DEFAULT_ATOMS: dict[str, AtomSpec] = {
    role: preset.to_spec() for role, preset in DEFAULT_PRESETS.items()
}

ATOM_TABLE = [
    {
        "role": preset.role,
        "framework": FRAMEWORK,
        "module": preset.module,
        "export": preset.export,
        "version": preset.version,
        "defaults": dict(preset.defaults),
    }
    for preset in DEFAULT_PRESETS.values()
]


def build_registry(
    *,
    extra_presets: Iterable[AtomPreset | AtomSpec]
    | Mapping[str, AtomPreset | AtomSpec]
    | None = None,
    overrides: Mapping[str, Mapping[str, object]] | None = None,
) -> AtomRegistry:
    """Create an AtomRegistry populated with SwarmaKit Svelte presets."""

    catalog = SwarmaAtomCatalog(DEFAULT_PRESETS, props_schema=AtomProps)

    if extra_presets:
        catalog = catalog.with_extra_presets(extra_presets)
    if overrides:
        for role, patch in overrides.items():
            try:
                catalog = catalog.with_overrides(role, **patch)
            except KeyError:
                continue

    return catalog.build_registry()


def build_default_registry() -> AtomRegistry:
    """Return an AtomRegistry populated with the default SwarmaKit Svelte presets."""

    return build_registry()


__all__ = [
    "FRAMEWORK",
    "SWARMAKIT_MODULE",
    "SWARMAKIT_VERSION",
    "PRESET_VERSION",
    "DEFAULT_PRESETS",
    "DEFAULT_ATOMS",
    "ATOM_TABLE",
    "build_registry",
    "build_default_registry",
]
