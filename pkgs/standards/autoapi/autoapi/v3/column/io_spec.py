# --- io_spec.py --------------------------------------------------------------
from dataclasses import dataclass, replace
from typing import Callable, Tuple, Literal
from .field_spec import FieldSpec as F


@dataclass(frozen=True)
class _PairedCfg:
    gen: Callable[[dict], object]  # ctx -> raw
    store: Callable[[object, dict], object]  # (raw, ctx) -> stored
    alias: str
    verbs: Tuple[str, ...]
    emit: str  # "pre_flush" | "post_refresh" | "readtime"
    alias_field: F
    mask_last: int | None


@dataclass(frozen=True)
class _AssembleCfg:
    sources: Tuple[str, ...]
    fn: Callable[[dict, dict], object]  # (payload, ctx) -> stored


@dataclass(frozen=True)
class _ReadtimeAlias:
    name: str
    fn: Callable[[object, dict], object]  # (obj, ctx) -> alias value
    verbs: Tuple[str, ...]
    alias_field: F
    mask_last: int | None


EmitPoint = Literal["pre_flush", "post_refresh", "pre_response", "readtime"]


@dataclass(frozen=True)
class Pair:
    raw: object
    stored: object


@dataclass(frozen=True)
class IOSpec:
    in_verbs: Tuple[str, ...] = ()
    out_verbs: Tuple[str, ...] = ()
    mutable_verbs: Tuple[str, ...] = ()
    alias_in: str | None = None
    alias_out: str | None = None
    sensitive: bool = False
    redact_last: int | None = None
    filter_ops: Tuple[str, ...] = ()
    sortable: bool = False
    allow_in: Callable[[str, dict], bool] | None = None
    allow_out: Callable[[str, dict], bool] | None = None
    _paired: _PairedCfg | None = None
    _assemble: _AssembleCfg | None = None
    _readtime_aliases: Tuple[_ReadtimeAlias, ...] = ()

    def assemble(self, sources, fn):
        """Return a new spec that derives a value from ``sources`` using ``fn``."""
        cfg = _AssembleCfg(sources=tuple(sources), fn=fn)
        return replace(self, _assemble=cfg)

    def paired(
        self,
        make,
        *,
        alias,
        verbs=("create",),
        emit: EmitPoint = "pre_flush",
        alias_field: F = F(py_type=str),
        mask_last: int | None = None,
    ):
        """Return a new spec with a paired field configuration."""

        def gen(ctx):
            return make(ctx).raw

        def store(raw, ctx):
            return make(ctx).stored

        cfg = _PairedCfg(
            gen=gen,
            store=store,
            alias=alias,
            verbs=tuple(verbs),
            emit=emit,
            alias_field=alias_field,
            mask_last=mask_last,
        )
        return replace(self, _paired=cfg)

    def alias_readtime(
        self,
        name,
        fn,
        *,
        verbs=("read", "list"),
        alias_field: F = F(py_type=str),
        mask_last: int | None = None,
    ):
        """Return a new spec with an additional read-time alias."""

        alias_cfg = _ReadtimeAlias(
            name=name,
            fn=fn,
            verbs=tuple(verbs),
            alias_field=alias_field,
            mask_last=mask_last,
        )
        return replace(self, _readtime_aliases=self._readtime_aliases + (alias_cfg,))
