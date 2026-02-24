"""Development-only example applications for the layout engine atoms package."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pkgutil

# Include the sibling ``examples`` directory (alongside ``src``) so that
# ``layout_engine_atoms.examples`` exposes the demo applications without having
# to ship them as part of the installable package.
_examples_root = Path(__file__).resolve().parent.parent.parent.parent / "examples"

# ``pkgutil.extend_path`` maintains compatibility with namespace packages and
# allows static type checkers to discover the modules during development.
__path__ = pkgutil.extend_path(__path__, __name__)  # type: ignore[name-defined]
if _examples_root.exists():
    __path__.append(str(_examples_root))  # type: ignore[attr-defined]


def iter_example_paths() -> Iterable[Path]:
    """Return the known filesystem locations that back the examples package."""
    if _examples_root.exists():
        yield _examples_root
