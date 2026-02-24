"""Atom registry for tiles (framework-agnostic).

- AtomSpec defines how a tile role maps to a client module/export and default props.
- AtomRegistry stores AtomSpec entries and can resolve merged props.
- bindings provides JSON (de)serialization and optional server-side render bindings (html/svg).
"""

from .spec import AtomSpec, merge_atom_props, validate_atom_role, validate_atom_module
from .base import IAtomRegistry
from .default import AtomRegistry, Atom
from .shortcuts import (
    define_atom,
    use_atom,
    apply_atom_defaults,
    derive_atom,
    make_atom,
)
from .decorators import atom_ctx, atom, validate_props
from .bindings import (
    atom_to_dict,
    atom_from_dict,
    registry_to_dict,
    registry_from_dict,
    ServerBindings,
    Renderer,
    HTMLRenderer,
    SVGRenderer,
)

__all__ = [
    "AtomSpec",
    "merge_atom_props",
    "validate_atom_role",
    "validate_atom_module",
    "IAtomRegistry",
    "Atom",
    "AtomRegistry",
    "define_atom",
    "use_atom",
    "apply_atom_defaults",
    "derive_atom",
    "make_atom",
    "atom_ctx",
    "atom",
    "validate_props",
    "atom_to_dict",
    "atom_from_dict",
    "registry_to_dict",
    "registry_from_dict",
    "ServerBindings",
    "Renderer",
    "HTMLRenderer",
    "SVGRenderer",
]
