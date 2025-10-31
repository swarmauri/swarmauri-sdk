from __future__ import annotations

import re
from typing import Iterable, Mapping

from layout_engine import AtomRegistry, AtomSpec

from ..swarma import AtomProps, SwarmaAtom

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


def _make_atom(name: str) -> SwarmaAtom:
    role = f"swarmakit:vue:{_slugify(name)}"
    spec = AtomSpec(
        role=role,
        module=SWARMAKIT_MODULE,
        export=name,
        version=SWARMAKIT_VERSION,
        defaults={},
    )
    return SwarmaAtom(spec=spec, props_schema=AtomProps)


_DEFAULT_ATOMS = tuple(_make_atom(name) for name in _COMPONENT_EXPORTS)

DEFAULT_PRESETS: dict[str, SwarmaAtom] = {
    atom.spec.role: atom for atom in _DEFAULT_ATOMS
}

DEFAULT_ATOMS: dict[str, AtomSpec] = {
    role: atom.to_spec() for role, atom in DEFAULT_PRESETS.items()
}

ATOM_TABLE = [
    {
        "role": atom.spec.role,
        "framework": FRAMEWORK,
        "module": atom.spec.module,
        "export": atom.spec.export,
        "version": atom.spec.version,
        "defaults": dict(atom.spec.defaults),
    }
    for atom in DEFAULT_PRESETS.values()
]


def build_registry(
    *,
    extra_presets: Iterable[SwarmaAtom] | Mapping[str, SwarmaAtom] | None = None,
    overrides: Mapping[str, Mapping[str, object]] | None = None,
) -> AtomRegistry:
    """Create an AtomRegistry populated with SwarmaKit Vue presets."""

    presets: dict[str, SwarmaAtom] = dict(DEFAULT_PRESETS)

    if extra_presets:
        if isinstance(extra_presets, Mapping):
            presets.update(extra_presets)
        else:
            presets.update({atom.spec.role: atom for atom in extra_presets})

    if overrides:
        for role, patch in overrides.items():
            if role not in presets:
                continue
            presets[role] = presets[role].with_overrides(**patch)

    registry = AtomRegistry()
    registry.register_many(atom.to_spec() for atom in presets.values())
    return registry


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
