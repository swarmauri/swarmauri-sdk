from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from layout_engine.authoring.widgets import _Base


@dataclass
class SwarmakitAvatar(_Base):
    def __init__(
        self,
        id: str,
        *,
        image_src: str = "https://example.com/avatar.png",
        initials: str = "AA",
        aria_label: str | None = None,
        **props: Any,
    ) -> None:
        merged = {
            "imageSrc": image_src,
            "initials": initials,
            "ariaLabel": aria_label or initials,
            **props,
        }
        super().__init__(id=id, role="avatar", props=merged)


@dataclass
class SwarmakitNotification(_Base):
    def __init__(
        self,
        id: str,
        *,
        message: str,
        notification_type: str = "success",
        is_dismissed: bool = False,
        **props: Any,
    ) -> None:
        merged = {
            "message": message,
            "notificationType": notification_type,
            "isDismissed": is_dismissed,
            **props,
        }
        super().__init__(id=id, role="notification", props=merged)


@dataclass
class SwarmakitProgressBar(_Base):
    def __init__(
        self,
        id: str,
        *,
        progress: float,
        disabled: bool = False,
        **props: Any,
    ) -> None:
        merged = {"progress": progress, "disabled": disabled, **props}
        super().__init__(id=id, role="progress", props=merged)


@dataclass
class SwarmakitDataGrid(_Base):
    def __init__(
        self,
        id: str,
        *,
        headers: Sequence[str],
        data: Iterable[Sequence[str]],
        pagination_enabled: bool = True,
        search_enabled: bool = False,
        resizable: bool = True,
        items_per_page: int = 5,
        **props: Any,
    ) -> None:
        merged = {
            "headers": list(headers),
            "data": [list(row) for row in data],
            "paginationEnabled": pagination_enabled,
            "searchEnabled": search_enabled,
            "resizable": resizable,
            "itemsPerPage": items_per_page,
            **props,
        }
        super().__init__(id=id, role="table", props=merged)


@dataclass
class SwarmakitTimeline(_Base):
    def __init__(
        self,
        id: str,
        *,
        items: Sequence[dict[str, Any]],
        active_index: int = 0,
        **props: Any,
    ) -> None:
        merged = {
            "items": [dict(item) for item in items],
            "activeIndex": active_index,
            **props,
        }
        super().__init__(id=id, role="timeline", props=merged)


__all__ = [
    "SwarmakitAvatar",
    "SwarmakitDataGrid",
    "SwarmakitNotification",
    "SwarmakitProgressBar",
    "SwarmakitTimeline",
]
