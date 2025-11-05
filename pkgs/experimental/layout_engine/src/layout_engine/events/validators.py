from __future__ import annotations
from typing import Any, Mapping, Set
from .spec import EventEnvelope

# ----- Allow lists (expanded) -----

SITE: Set[str] = {
    "site:load",
    "site:ready",
    "site:error",
    "site:navigate",
    "site:theme:change",
    "site:locale:change",
    "ws_open",
    "ws_message",
    "ws_close",
    "ws_error",
}
SLOT: Set[str] = {"slot:mount", "slot:unmount", "slot:visibilitychange", "slot:resize"}
PAGE: Set[str] = {
    "page:load",
    "page:unload",
    "page:params:change",
    "page:resize",
    "page:refresh",
    "page:patch-applied",
    "page:export",
    "page:scroll",
}
GRID: Set[str] = {
    "grid:layout:compute-start",
    "grid:layout:computed",
    "grid:breakpoint:change",
    "grid:reflow",
    "grid:resize",
    "grid:scroll",
    # rearrange variants covered via wildcard matcher too
    "grid:tile:rearrange:start",
    "grid:tile:rearrange:over",
    "grid:tile:rearrange:commit",
    "grid:tile:rearrange:cancel",
}
TILE: Set[str] = {
    "tile:focus",
    "tile:blur",
    "tile:hover",
    "tile:contextmenu",
    "tile:visibilitychange",
    "tile:resize",
    "tile:maximize",
    "tile:minimize",
    "tile:refresh",
    "tile:export",
    "tile:dragstart",
    "tile:dragover",
    "tile:drop",
    "tile:dragend",
}
ATOM: Set[str] = {
    # pointer*
    "pointerdown",
    "pointerup",
    "pointermove",
    "pointerenter",
    "pointerleave",
    "pointerover",
    "pointerout",
    "pointercancel",
    "gotpointercapture",
    "lostpointercapture",
    # basic mouse/wheel/context for parity
    "click",
    "dblclick",
    "contextmenu",
    "wheel",
    # keys & composition*
    "keydown",
    "keyup",
    "compositionstart",
    "compositionupdate",
    "compositionend",
    # forms
    "beforeinput",
    "input",
    "change",
    "submit",
    "reset",
    # focus/blur
    "focus",
    "blur",
    # selection
    "select",
    "selectionchange",
    # clipboard
    "copy",
    "cut",
    "paste",
    # drag*
    "dragstart",
    "drag",
    "dragenter",
    "dragover",
    "dragleave",
    "dragend",
    "drop",
    # media*
    "play",
    "pause",
    "seeking",
    "seeked",
    "timeupdate",
    "volumechange",
    "ratechange",
    "ended",
    "loadeddata",
    "loadedmetadata",
    "canplay",
    "canplaythrough",
    "stalled",
    "suspend",
    "waiting",
    "error",
    "progress",
    "durationchange",
    "emptied",
    "abort",
}

ALLOW = {
    "site": SITE,
    "slot": SLOT,
    "page": PAGE,
    "grid": GRID,
    "tile": TILE,
    "atom": ATOM,
}

_CHANNEL_REGISTRY: dict[str, dict[str, Any]] = {}


def register_channels(
    channels: Mapping[str, Mapping[str, Any]] | list[Mapping[str, Any]],
) -> None:
    if isinstance(channels, Mapping):
        iterator = channels.values()
    else:
        iterator = channels
    for entry in iterator:
        channel_id = entry.get("id")
        if not channel_id:
            continue
        _CHANNEL_REGISTRY[str(channel_id)] = dict(entry)


def clear_channels() -> None:
    _CHANNEL_REGISTRY.clear()


def get_channel(channel_id: str) -> dict[str, Any] | None:
    return _CHANNEL_REGISTRY.get(channel_id)


# Wildcard families per scope
def _wildcards(scope: str) -> list[str]:
    if scope == "site":
        return ["site:auth:"]
    if scope == "slot":
        return ["slot:remote:"]
    if scope == "grid":
        return ["grid:tile:rearrange:"]
    if scope == "tile":
        return ["tile:drag"]
    if scope == "atom":
        return [
            "pointer",  # pointer*
            "composition",  # composition*
            "drag",  # drag*
            # media* covered by explicit list above; keep here for completeness
        ]
    return []


class ValidationError(Exception):
    """Raised when an event envelope fails validation."""

    pass


def is_allowed(scope: str, etype: str) -> bool:
    # Exact
    if etype in ALLOW.get(scope, set()):
        return True
    # Wildcards
    for pref in _wildcards(scope):
        if etype.startswith(pref):
            return True
    # Special ws:* for site
    if scope == "site" and etype.startswith("ws_"):
        return True
    return False


def allowed_types_for(scope: str) -> set[str]:
    base = set(ALLOW.get(scope, set()))
    # Add documented wildcard hints (not exhaustive enumeration)
    base.update({w + "*" for w in _wildcards(scope)})
    if scope == "site":
        base.add("ws:*")
    return base


def validate_envelope(e: dict[str, Any]) -> EventEnvelope:
    for k in ("scope", "type", "ts", "request_id"):
        if k not in e:
            raise ValidationError(f"missing field: {k}")
    scope = e["scope"]
    etype = e["type"]
    if scope not in ALLOW:
        raise ValidationError(f"unknown scope: {scope}")
    if not is_allowed(scope, etype):
        raise ValidationError(f"event '{etype}' not allowed for scope '{scope}'")
    channel_id = e.get("channel")
    if channel_id is not None:
        channel_def = _CHANNEL_REGISTRY.get(str(channel_id))
        if channel_def is None:
            raise ValidationError(f"unknown channel: {channel_id}")
        expected_scope = channel_def.get("scope")
        if expected_scope and expected_scope != scope:
            raise ValidationError(
                f"channel '{channel_id}' expects scope '{expected_scope}' but received '{scope}'"
            )

    return EventEnvelope(
        scope=scope,
        type=etype,
        page_id=e.get("page_id"),
        slot=e.get("slot"),
        tile_id=e.get("tile_id"),
        ts=e["ts"],
        request_id=e["request_id"],
        target=e.get("target") or {},
        payload=e.get("payload") or {},
        channel=str(channel_id) if channel_id is not None else None,
    )


def route_topic(ev: EventEnvelope) -> str:
    if ev.channel:
        channel_def = _CHANNEL_REGISTRY.get(ev.channel)
        if channel_def:
            template = channel_def.get("topic")
            if template:
                context = {
                    "scope": ev.scope,
                    "type": ev.type,
                    "page_id": ev.page_id or "",
                    "slot": ev.slot or "",
                    "tile_id": ev.tile_id or "",
                    "channel": ev.channel,
                }
                context.update(ev.target or {})
                try:
                    return template.format(**context)
                except Exception:
                    return template

    if ev.scope == "site":
        return "site"
    if ev.scope == "page":
        return f"page:{ev.page_id}"
    if ev.scope == "slot":
        return f"slot:{ev.page_id}:{ev.slot}"
    if ev.scope == "grid":
        return f"grid:{ev.page_id}"
    if ev.scope == "tile":
        return f"tile:{ev.page_id}:{ev.tile_id}"
    if ev.scope == "atom":
        key = (ev.target or {}).get("key", "_")
        return f"atom:{ev.page_id}:{ev.tile_id}:{key}"
    raise ValidationError("unroutable")
