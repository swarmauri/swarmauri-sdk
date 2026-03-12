from __future__ import annotations

from pathlib import Path
import re

from tigrbl_atoms import types as atom_types
from tigrbl_runtime.executors.types import _Ctx


_PROMOTE_TARGET_RE = re.compile(r"ctx\.promote\((\w+)")


def _discover_promote_targets() -> set[str]:
    atoms_root = (
        Path(__file__).resolve().parents[2] / "tigrbl_atoms" / "tigrbl_atoms" / "atoms"
    )
    targets: set[str] = set()
    for py_file in atoms_root.rglob("*.py"):
        for match in _PROMOTE_TARGET_RE.finditer(py_file.read_text()):
            targets.add(match.group(1))
    return targets


def test_runtime_ctx_can_promote_to_all_atom_ctx_targets() -> None:
    targets = _discover_promote_targets()
    assert targets, "expected to discover ctx.promote targets in atom modules"

    ctx = _Ctx.ensure(request=None, db=None, seed={})
    for target_name in sorted(targets):
        target = getattr(atom_types, target_name, None)
        assert target is not None, f"missing target type: {target_name}"

        promoted = ctx.promote(target)
        assert isinstance(promoted, target)
