from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import tigrbl_atoms.events as events
import tigrbl_atoms.phases as phases
from tigrbl_atoms.stages import is_monotonic_transition, stage_ordinal


@dataclass(frozen=True)
class AtomStageSignature:
    path: Path
    anchor: str
    stage_in: type[object]
    stage_out: type[object]


def _standards_dir() -> Path:
    return Path(__file__).resolve().parents[4]


def _atoms_dir() -> Path:
    return _standards_dir() / "tigrbl_atoms" / "tigrbl_atoms" / "atoms"


def _parse_signature(module_path: Path) -> AtomStageSignature | None:
    tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))

    anchor: str | None = None
    stage_in_name: str | None = None
    stage_out_name: str | None = None

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ANCHOR":
                    if isinstance(node.value, ast.Attribute) and isinstance(
                        node.value.value, ast.Name
                    ):
                        if node.value.value.id == "_ev":
                            anchor = getattr(events, node.value.attr)
                    elif isinstance(node.value, ast.Constant) and isinstance(
                        node.value.value, str
                    ):
                        anchor = node.value.value
        if isinstance(node, ast.ClassDef) and node.name == "AtomImpl":
            for base in node.bases:
                if not isinstance(base, ast.Subscript):
                    continue
                if not isinstance(base.value, ast.Name) or base.value.id != "Atom":
                    continue
                if not isinstance(base.slice, ast.Tuple) or len(base.slice.elts) != 2:
                    continue
                left, right = base.slice.elts
                if isinstance(left, ast.Name) and isinstance(right, ast.Name):
                    stage_in_name = left.id
                    stage_out_name = right.id

    if anchor is None or stage_in_name is None or stage_out_name is None:
        return None

    import tigrbl_atoms.stages as stages

    return AtomStageSignature(
        path=module_path,
        anchor=anchor,
        stage_in=getattr(stages, stage_in_name),
        stage_out=getattr(stages, stage_out_name),
    )


def _all_atom_signatures() -> list[AtomStageSignature]:
    signatures: list[AtomStageSignature] = []
    for module_path in sorted(_atoms_dir().rglob("*.py")):
        if module_path.name == "__init__.py":
            continue
        sig = _parse_signature(module_path)
        if sig is not None:
            signatures.append(sig)
    return signatures


def test_every_atom_signature_stays_within_anchor_window() -> None:
    signatures = _all_atom_signatures()
    assert signatures, "No atom signatures discovered."

    violations: list[str] = []
    for sig in signatures:
        anchor_info = events.get_anchor_info(sig.anchor)
        phase_info = phases.phase_info(anchor_info.phase)

        atom_in = stage_ordinal(sig.stage_in)
        atom_out = stage_ordinal(sig.stage_out)
        phase_in = stage_ordinal(phase_info.stage_in)
        phase_out = stage_ordinal(phase_info.stage_out)

        if atom_in < phase_in:
            violations.append(
                f"{sig.path}: atom enters before phase {phase_info.name} "
                f"({sig.stage_in.__name__} < {phase_info.stage_in.__name__})"
            )
        if atom_out > phase_out:
            violations.append(
                f"{sig.path}: atom exits after phase {phase_info.name} "
                f"({sig.stage_out.__name__} > {phase_info.stage_out.__name__})"
            )
        if not is_monotonic_transition(sig.stage_in, sig.stage_out):
            violations.append(
                f"{sig.path}: non-monotonic atom signature "
                f"({sig.stage_in.__name__} -> {sig.stage_out.__name__})"
            )

    assert not violations, "\n".join(violations)
