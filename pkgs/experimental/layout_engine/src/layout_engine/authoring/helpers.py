from __future__ import annotations

import importlib
from typing import Callable, Iterable, Mapping, MutableMapping, Sequence

from ..atoms import AtomRegistry
from ..grid.spec import GridSpec
from ..manifest.spec import ChannelManifest, WsRouteManifest
from ..manifest.default import ManifestBuilder
from ..site.spec import SiteSpec


def register_swarma_atoms(
    registry: AtomRegistry,
    *,
    catalog: str = "vue",
    extra_presets: Iterable[Mapping[str, object]] | None = None,
) -> AtomRegistry:
    """Load SwarmaKit presets into the provided registry.

    Imports ``layout_engine_atoms`` lazily to keep the dependency optional.
    """

    try:
        catalog_module = importlib.import_module("layout_engine_atoms.catalog")
    except ImportError as exc:
        raise RuntimeError(
            "layout_engine_atoms is required to register SwarmaKit presets"
        ) from exc

    builder = getattr(catalog_module, "build_catalog", None)
    if builder is None:
        raise RuntimeError("layout_engine_atoms.catalog missing build_catalog()")

    cat = builder(catalog)
    for preset in cat.presets():
        registry.register(preset.to_spec())

    if extra_presets:
        for preset_data in extra_presets:
            preset = cat.get(preset_data.get("role"))
            registry.override(preset.role, **dict(preset_data))

    return registry


def grid_token_snapshot(spec: GridSpec) -> MutableMapping[str, object]:
    """Return a dict describing the grid token configuration for analytics."""

    snapshot: MutableMapping[str, object] = {}
    if getattr(spec, "tokens", None):
        snapshot["tokens"] = dict(spec.tokens)
    if getattr(spec, "baseline_unit", None) is not None:
        snapshot["baseline_unit"] = int(spec.baseline_unit)
    snapshot["columns"] = len(spec.columns)
    snapshot["gap_x"] = spec.gap_x
    snapshot["gap_y"] = spec.gap_y
    return snapshot


def build_site_manifest(
    site: SiteSpec,
    page_compilers: Mapping[str, Callable[[], Mapping[str, object]]],
    *,
    channels: Sequence[ChannelManifest] | None = None,
    ws_routes: Sequence[WsRouteManifest] | None = None,
) -> dict[str, object]:
    """Compile a mapping of page ids to manifests with shared site metadata."""

    manifests: dict[str, object] = {}
    builder = ManifestBuilder()
    for page in site.pages:
        compiler = page_compilers.get(page.id)
        if compiler is None:
            continue
        view_model = compiler()
        manifest = builder.build(
            view_model,
            active_page=page.id,
            site=site,
            channels=channels,
            ws_routes=ws_routes,
        )
        manifests[page.id] = manifest
    return manifests
