from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = PACKAGE_ROOT / "src/layout_engine_atoms/runtime/core"


def run_node(script: str) -> dict:
    try:
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise AssertionError(
            f"Node execution failed with code {exc.returncode}: {exc.stderr}"
        ) from exc
    stdout = result.stdout.strip()
    assert stdout, f"expected Node script to emit JSON, got: {result.stdout!r}"
    return json.loads(stdout)


def test_theme_controller_apply():
    theme_path = (CORE_DIR / "theme.js").as_uri()
    script = textwrap.dedent(
        f"""
        import {{ createThemeController }} from "{theme_path}";

        const controller = createThemeController({{
          className: "base",
          style: {{ background: "#fff" }},
          tokens: {{ accent: "#123456" }},
        }});

        controller.apply({{
          className: "hero",
          style: {{ background: "#111" }},
          tokens: {{ accent: "#00ffaa", surface: "#f5f5f5" }},
        }});

        console.log(JSON.stringify(controller.state));
        """
    )
    data = run_node(script)
    assert data["className"] == "hero"
    assert data["style"]["background"] == "#111"
    assert data["tokens"]["accent"] == "#00ffaa"
    assert data["tokens"]["surface"] == "#f5f5f5"


def test_runtime_state_fetch_and_patch():
    state_path = (CORE_DIR / "state.js").as_uri()
    manifest_json = json.dumps(
        {
            "kind": "layout_manifest",
            "version": "2025.01",
            "viewport": {"width": 1280, "height": 720},
            "grid": {"row_height": 180, "gap_x": 16, "gap_y": 16},
            "tiles": [
                {
                    "id": "hero",
                    "role": "layout:card",
                    "frame": {"x": 0, "y": 0, "w": 1280, "h": 180},
                    "props": {"title": "Initial"},
                }
            ],
            "pages": [
                {
                    "id": "overview",
                    "label": "Overview",
                    "tiles": [
                        {
                            "id": "hero",
                            "role": "layout:card",
                            "frame": {"x": 0, "y": 0, "w": 1280, "h": 180},
                            "props": {"title": "Initial"},
                        }
                    ],
                }
            ],
        }
    )
    patch_json = json.dumps(
        {
            "tiles": [
                {
                    "id": "hero",
                    "role": "layout:card",
                    "frame": {"x": 0, "y": 0, "w": 1280, "h": 180},
                    "props": {"title": "Welcome"},
                }
            ],
            "pages": [
                {
                    "id": "overview",
                    "tiles": [
                        {
                            "id": "hero",
                            "role": "layout:card",
                            "frame": {"x": 0, "y": 0, "w": 1280, "h": 180},
                            "props": {"title": "Welcome"},
                        }
                    ],
                }
            ],
        }
    )
    script = textwrap.dedent(
        f"""
        import {{ createRuntimeState }} from "{state_path}";

        const runtime = createRuntimeState({{
          initialPageId: "overview",
        }});

        const manifest = {manifest_json};
        const patch = {patch_json};

        runtime.setFetcher(async () => {{
          return {{
            ok: true,
            status: 200,
            statusText: "OK",
            json: async () => manifest,
          }};
        }});

        await runtime.fetchManifest("https://example.com/dashboard/manifest.json");
        runtime.applyPatch(patch);

        console.log(JSON.stringify({{
          pageId: runtime.state.pageId,
          tileCount: runtime.state.view.tiles.length,
          title: runtime.state.view.tiles[0]?.props?.title ?? null,
        }}));
        """
    )
    data = run_node(script)
    assert data["pageId"] == "overview"
    assert data["tileCount"] == 1
    assert data["title"] == "Welcome"


def test_derive_events_url():
    core_path = (CORE_DIR / "index.js").as_uri()
    script = textwrap.dedent(
        f"""
        import {{ deriveEventsUrl }} from "{core_path}";

        const derived = deriveEventsUrl({{
          manifestUrl: "https://demo.example.com/dashboard/manifest.json",
        }});

        const explicit = deriveEventsUrl({{
          explicitUrl: "wss://api.example.com/events",
        }});

        console.log(JSON.stringify({{ derived, explicit }}));
        """
    )
    data = run_node(script)
    assert data["derived"].endswith("/dashboard/events")
    assert data["derived"].startswith("wss://demo.example.com/")
    assert data["explicit"] == "wss://api.example.com/events"


def test_swiss_grid_theme_export():
    core_path = (CORE_DIR / "index.js").as_uri()
    script = textwrap.dedent(
        f"""
        import {{ SWISS_GRID_THEME }} from "{core_path}";

        console.log(JSON.stringify(SWISS_GRID_THEME));
        """
    )
    data = run_node(script)
    tokens = data.get("tokens", {})
    assert data.get("className") == "le-theme-swiss-grid"
    assert tokens.get("space-4") == "1rem"
    assert tokens.get("font-size-base")
