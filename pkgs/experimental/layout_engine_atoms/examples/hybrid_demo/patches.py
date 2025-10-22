from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict, List


class PatchBuilder:
    """Build manifest patches for the incidents tile."""

    def __init__(self, manifest_factory: Callable[[], Dict[str, Any]]):
        manifest = manifest_factory()
        tiles = manifest.get("tiles", [])
        self.tiles_template = [deepcopy(tile) for tile in tiles]
        incidents = next(
            (tile for tile in tiles if tile.get("id") == "tile_incidents"), None
        )
        self.tile_id = incidents.get("id") if incidents else None

    def build_patch(self, rows: List[Dict[str, str]]) -> Dict[str, Any]:
        tiles: List[Dict[str, Any]] = []
        for template in self.tiles_template:
            tile = deepcopy(template)
            if self.tile_id and tile.get("id") == self.tile_id:
                tile.setdefault("props", {})["rows"] = rows
            tiles.append(tile)
        return {"tiles": tiles}


class MpaPatchBuilder(PatchBuilder):
    def __init__(self, manifest_factory: Callable[[], Dict[str, Any]]):
        super().__init__(manifest_factory)
        manifest = manifest_factory()
        root_tile = next(
            (
                tile
                for tile in manifest.get("tiles", [])
                if tile.get("id") == "tile_incidents"
            ),
            None,
        )
        self.tile_template = deepcopy(root_tile) if root_tile else None

        pages = manifest.get("pages", [])
        page = next(page for page in pages if page.get("id") == "incidents")
        page_tile = next(
            tile for tile in page.get("tiles", []) if tile.get("id") == "tile_incidents"
        )
        self.page_tile_template = deepcopy(page_tile)
        self.page_tile_id = page_tile.get("id")
        self.pages_template = [deepcopy(p) for p in pages]

    def build_patch(self, rows: List[Dict[str, str]]) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        tiles = []
        for template in self.tiles_template:
            tile = deepcopy(template)
            if tile.get("id") == self.tile_id:
                tile.setdefault("props", {})["rows"] = rows
            tiles.append(tile)
        if tiles:
            payload["tiles"] = tiles

        page_tile = deepcopy(self.page_tile_template)
        page_tile.setdefault("props", {})["rows"] = rows
        pages: List[Dict[str, Any]] = []
        for template in self.pages_template:
            page_copy = deepcopy(template)
            if page_copy.get("id") == "incidents":
                updated_tiles: List[Dict[str, Any]] = []
                for tile in template.get("tiles", []):
                    if tile.get("id") == self.page_tile_id:
                        replacement = deepcopy(page_tile)
                        updated_tiles.append(replacement)
                    else:
                        updated_tiles.append(deepcopy(tile))
                page_copy["tiles"] = updated_tiles
            pages.append(page_copy)
        payload["pages"] = pages
        return payload
