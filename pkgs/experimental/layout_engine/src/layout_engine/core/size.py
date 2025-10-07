from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Literal, Mapping, Optional

Unit = Literal["px", "fr", "%"]


class SizeToken(str, Enum):
    xxs = "xxs"
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"  # noqa: E741 - short token name retained for backwards compat
    xl = "xl"
    xxl = "xxl"


DEFAULT_TOKEN_WEIGHTS: dict[SizeToken, float] = {
    SizeToken.xxs: 0.5,
    SizeToken.xs: 0.75,
    SizeToken.s: 1.0,
    SizeToken.m: 1.5,
    SizeToken.l: 2.0,
    SizeToken.xl: 3.0,
    SizeToken.xxl: 4.0,
}


@dataclass(frozen=True)
class Size:
    value: float
    unit: Unit = "px"
    min_px: int = 0
    max_px: Optional[int] = None


def tokens_to_fr_sizes(tokens: Iterable[SizeToken], *, min_px: int = 200) -> list[Size]:
    """Convert size tokens to FR-based Size descriptors."""
    sizes: list[Size] = []
    for token in tokens:
        tok = SizeToken(token)
        sizes.append(Size(value=DEFAULT_TOKEN_WEIGHTS[tok], unit="fr", min_px=min_px))
    return sizes


def resolve_column_widths(
    tracks: list[Size], viewport_width: int, gap: int
) -> list[int]:
    """Resolve a sequence of Size tracks into concrete pixel widths."""
    n = len(tracks)
    if n == 0:
        return []

    total_gap = max(0, n - 1) * max(0, gap)
    available = max(0, int(viewport_width) - total_gap)

    resolved = [0.0] * n
    fixed_total = 0.0
    fr_indices: list[int] = []
    total_fr = 0.0

    for idx, size in enumerate(tracks):
        unit = size.unit
        if unit == "px":
            resolved[idx] = float(size.value)
            fixed_total += resolved[idx]
        elif unit == "%":
            width = available * float(size.value) / 100.0
            resolved[idx] = width
            fixed_total += width
        elif unit == "fr":
            fr_indices.append(idx)
            total_fr += float(size.value)
        else:
            raise ValueError(f"Unknown size unit '{unit}'")

    remaining = max(0.0, available - fixed_total)
    if fr_indices:
        share = remaining / total_fr if total_fr > 0 else 0.0
        for idx in fr_indices:
            resolved[idx] = share * float(tracks[idx].value)

    widths: list[int] = []
    for idx, size in enumerate(tracks):
        w = int(round(resolved[idx]))
        w = max(w, size.min_px)
        if size.max_px is not None:
            w = min(w, size.max_px)
        widths.append(max(w, 0))

    drift = available - sum(widths)
    i = 0
    while drift != 0 and widths:
        step = 1 if drift > 0 else -1
        idx = i % n
        candidate = widths[idx] + step
        if candidate >= tracks[idx].min_px and (
            tracks[idx].max_px is None or candidate <= tracks[idx].max_px
        ):
            widths[idx] = candidate
            drift -= step
        i += 1

    return widths


def parse_size(value: Any) -> Size:
    """Parse common representations into a :class:`Size` instance."""
    if isinstance(value, Size):
        return value
    if isinstance(value, Mapping):
        return Size(
            value=float(value.get("value", 0)),
            unit=str(value.get("unit", "px")),
            min_px=int(value.get("min_px", 0)),
            max_px=(int(value["max_px"]) if value.get("max_px") is not None else None),
        )
    if isinstance(value, (tuple, list)) and len(value) >= 2:
        val, unit = value[0], value[1]
        return Size(value=float(val), unit=str(unit))
    if isinstance(value, (int, float)):
        return Size(value=float(value), unit="px")
    if isinstance(value, str):
        text = value.strip().lower()
        if text.endswith("fr"):
            num = text[:-2] or "1"
            return Size(value=float(num), unit="fr")
        if text.endswith("px"):
            num = text[:-2] or "0"
            return Size(value=float(num), unit="px")
        if text.endswith("%"):
            num = text[:-1] or "0"
            return Size(value=float(num), unit="%")
        raise ValueError(f"Unrecognized size string '{value}'")
    raise TypeError(f"Cannot parse size from value of type {type(value)!r}")
