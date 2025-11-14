from __future__ import annotations

import re
from typing import Iterable, Mapping

from layout_engine import AtomRegistry, AtomSpec

from ..spec import AtomPreset
from ..swarma import AtomProps, SwarmaAtomCatalog

FRAMEWORK = "vue"
SWARMAKIT_MODULE = "@swarmakit/vue"
SWARMAKIT_VERSION = "0.0.22"
PRESET_VERSION = SWARMAKIT_VERSION

_COMPONENT_EXPORTS: tuple[str, ...] = (
    "ThreeSixtyDegreeImageViewer",
    "Accordion",
    "ActionableList",
    "ActivityIndicators",
    "AdminViewScheduler",
    "AudioPlayer",
    "AudioPlayerAdvanced",
    "AudioWaveformDisplay",
    "Avatar",
    "Badge",
    "BadgeWithCounts",
    "BatteryLevelIndicator",
    "BetSlider",
    "BottomNavigationBar",
    "BreadcrumbWithDropdowns",
    "Breadcrumbs",
    "BrushTool",
    "Button",
    "CalendarView",
    "CallButton",
    "Canvas",
    "Captcha",
    "CardActions",
    "CardBadge",
    "CardBody",
    "CardFooter",
    "CardHeader",
    "CardImage",
    "CardbasedList",
    "Carousel",
    "ChatBubble",
    "CheckList",
    "Checkbox",
    "Chips",
    "CollapsibleMenuList",
    "ColorPicker",
    "ColumnVisibilityToggle",
    "CommandPalette",
    "CommunityCards",
    "ContextualList",
    "ContextualNavigation",
    "CountdownTimer",
    "DarkModeToggle",
    "DataExportButton",
    "DataFilterPanel",
    "DataGrid",
    "DataImportDialog",
    "DataSummary",
    "DataTable",
    "DateAndTimePicker",
    "DatePicker",
    "DealerButton",
    "DeckOfCards",
    "DiscardPile",
    "DragAndDropScheduler",
    "DropdownMenu",
    "EditableDataTable",
    "EmbeddedMediaIframe",
    "EmojiReactionPoll",
    "EraserTool",
    "EventDetailsDialog",
    "EventFilterBar",
    "EventReminderSystem",
    "ExpandableList",
    "FavoritesList",
    "FieldEditableDataTable",
    "FileInputWithPreview",
    "FileUpload",
    "FillTool",
    "FilterableList",
    "FlipCard",
    "FloatingActionButton",
    "FoldButton",
    "GroupedList",
    "HandOfCards",
    "IconButton",
    "ImageChoicePoll",
    "ImageSlider",
    "InteractiveMediaMap",
    "InteractivePollResults",
    "LayerPanel",
    "LiveResultsPoll",
    "LiveStreamPlayer",
    "LoadMoreButtonInList",
    "LoadingBarsWithSteps",
    "LoadingSpinner",
    "MediaGallery",
    "MultipleChoicePoll",
    "MultiselectList",
    "Notification",
    "NotificationBellIcon",
    "NumberInputWithIncrement",
    "NumberedList",
    "OpenEndedPoll",
    "Pagination",
    "PaginationControl",
    "PasswordConfirmationField",
    "PinnedList",
    "PlayingCard",
    "PodcastPlayer",
    "PokerChips",
    "PokerHand",
    "PokerTable",
    "PokerTimer",
    "Pot",
    "ProgressBar",
    "ProgressCircle",
    "PublicViewCalendar",
    "RadioButton",
    "RaiseButton",
    "RangeSlider",
    "RankingPoll",
    "RatingStars",
    "RecurringEventScheduler",
    "RichTextEditor",
    "RulerAndGuides",
    "ScheduleCRUDPanel",
    "ScrollableList",
    "SearchBar",
    "SearchBarWithSuggestions",
    "SearchInputWithFilterOptions",
    "SearchWithAutocomplete",
    "SelectableListWithItemDetails",
    "ShapeLibrary",
    "ShapeTool",
    "SignalStrengthIndicator",
    "SingleChoicePoll",
    "SkeletonLoading",
    "Slider",
    "SliderPoll",
    "SortControl",
    "SortableList",
    "SortableTable",
    "StarRatingPoll",
    "StatusDots",
    "Stepper",
    "SystemAlertGlobalNotificationBar",
    "Tabs",
    "TaskCompletionCheckList",
    "TextTool",
    "Textarea",
    "ThumbsUpThumbsDownPoll",
    "TimelineAdjuster",
    "TimelineList",
    "Toast",
    "ToggleSwitch",
    "TreeviewList",
    "UndoRedoButtons",
    "Upload",
    "ValidationMessages",
    "Video",
    "VideoPlayer",
    "VirtualizedList",
    "VisualCueForAccessibilityFocusIndicator",
    "WinningHandDisplay",
    "YesNoPoll",
    "ZoomTool",
)


def _slugify(name: str) -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    text = re.sub(r"([A-Z])([A-Z][a-z])", r"\1-\2", text)
    return text.replace("_", "-").lower()


def _make_preset(name: str) -> AtomPreset:
    role = f"swarmakit:vue:{_slugify(name)}"
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

def _with_event_mappings(preset: AtomPreset) -> AtomPreset:
    """Attach event-aware prop hints to specific atoms."""

    event_maps: dict[str, dict[str, object]] = {
        "swarmakit:vue:button": {
            "events": {
                "primary": {
                    "listener": "onClick",
                    "loadingProp": "loading",
                    "disabledProp": "disabled",
                },
            }
        },
        "swarmakit:vue:cardbased-list": {
            "events": {
                "select": {"listener": "onSelect"},
                "action": {"listener": "onAction"},
            }
        },
        "swarmakit:vue:actionable-list": {
            "events": {
                "primary": {"listener": "onPrimaryAction"},
                "secondary": {"listener": "onSecondaryAction"},
            }
        },
    }
    mapping = event_maps.get(preset.role)
    if not mapping:
        return preset
    merged_defaults = {**preset.defaults, **mapping}
    return AtomPreset(
        role=preset.role,
        module=preset.module,
        export=preset.export,
        version=preset.version,
        defaults=merged_defaults,
        framework=preset.framework,
        package=preset.package,
        family=preset.family,
        registry=preset.registry,
    )


DEFAULT_PRESETS: dict[str, AtomPreset] = {
    preset.role: _with_event_mappings(preset) for preset in _DEFAULT_PRESETS
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
    """Create an AtomRegistry populated with SwarmaKit Vue presets."""

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
    """Return an AtomRegistry populated with the default SwarmaKit Vue presets."""

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
