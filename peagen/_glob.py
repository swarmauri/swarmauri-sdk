from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence, Union

PathLike = Union[str, Path]


def expand_globs(
    patterns: Union[PathLike, Sequence[PathLike]],
    base: PathLike = ".",
) -> List[Path]:
    """Expand dir, multi-file, and single-file globs to resolved file paths."""
    base_path = Path(base)
    if isinstance(patterns, (str, Path)):
        items: Sequence[PathLike] = (patterns,)
    else:
        items = patterns

    seen: set[Path] = set()
    out: List[Path] = []

    for raw in items:
        for path in _expand_one(str(raw), base_path):
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                out.append(resolved)

    out.sort()
    return out


def _has_magic(text: str) -> bool:
    return any(ch in text for ch in "*?[")


def _expand_one(pattern: str, base: Path) -> Iterable[Path]:
    path = Path(pattern)

    if not _has_magic(pattern):
        target = path if path.is_absolute() else base / path
        if target.is_file():
            yield target
        elif target.is_dir():
            yield from (p for p in sorted(target.rglob("*")) if p.is_file())
        return

    if path.is_absolute():
        parts = path.parts
        idx = next(
            (i for i, part in enumerate(parts) if _has_magic(part)),
            len(parts),
        )
        root = Path(*parts[:idx]) if idx else Path(path.anchor)
        rest = str(Path(*parts[idx:])) if idx < len(parts) else "*"
        matches = root.glob(rest)
    else:
        matches = base.glob(pattern)

    for match in sorted(matches):
        if match.is_file():
            yield match
        elif match.is_dir():
            yield from (p for p in sorted(match.rglob("*")) if p.is_file())
