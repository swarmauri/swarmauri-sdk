from __future__ import annotations

import os
from importlib.resources import files

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .manifests import DEFAULT_PAGE_ID, build_manifest, resolve_page_by_route

APP_TITLE = "Swarmauri Mission Control"
MANIFEST_ENDPOINT = "/manifest.json"

_LAYOUT_ENGINE_DIST = os.fspath(
    files("layout_engine_atoms.runtime.vue.assets") / "layout-engine-vue"
)
_SWARMA_VUE_DIST = os.fspath(
    files("layout_engine_atoms.runtime.vue.assets") / "swarma-vue"
)

app = FastAPI(title="Layout Engine MPA Demo", docs_url=None)

app.mount(
    "/static/layout-engine-vue",
    StaticFiles(directory=_LAYOUT_ENGINE_DIST, html=False),
    name="layout-engine-vue",
)
app.mount(
    "/static/swarma-vue",
    StaticFiles(directory=_SWARMA_VUE_DIST, html=False),
    name="swarma-vue",
)


def _render_shell(*, title: str, page_id: str) -> str:
    """Return the base HTML shell with the requested page baked in."""

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <link rel="stylesheet" href="/static/swarma-vue/style.css" />
    <script type="importmap">
      {{
        "imports": {{
          "vue": "https://cdn.jsdelivr.net/npm/vue@3/dist/vue.esm-browser.js",
          "eventemitter3": "https://cdn.jsdelivr.net/npm/eventemitter3@5/dist/eventemitter3.esm.js",
          "@swarmakit/vue": "/static/swarma-vue/vue.js"
        }}
      }}
    </script>
    <style>
      :root {{
        color-scheme: dark;
      }}
      body {{
        margin: 0;
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        background: radial-gradient(circle at 18% -12%, rgba(56,189,248,0.42), rgba(2,6,23,1) 60%);
        color: #e2e8f0;
        min-height: 100vh;
      }}
      main {{
        max-width: 1440px;
        margin: 0 auto;
        padding: 2.5rem 2rem 4.25rem;
      }}
      .demo-shell {{
        position: relative;
        background: linear-gradient(155deg, rgba(15,23,42,0.9), rgba(2,6,23,0.94));
        border-radius: 30px;
        border: 1px solid rgba(148,163,184,0.18);
        padding: 2.4rem 2.8rem 3.1rem;
        box-shadow: 0 46px 140px rgba(2, 6, 23, 0.78);
        overflow: hidden;
      }}
      .demo-shell::before {{
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 24% 20%, rgba(56,189,248,0.24), transparent 55%);
        pointer-events: none;
      }}
      .demo-shell::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 85% 0%, rgba(99,102,241,0.18), transparent 40%);
        pointer-events: none;
      }}
      .demo-content {{
        position: relative;
        z-index: 1;
      }}
      .demo-header {{
        display: flex;
        justify-content: space-between;
        gap: 1.75rem;
        align-items: flex-start;
      }}
      .demo-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-size: 0.7rem;
        padding: 0.4rem 0.85rem;
        border-radius: 999px;
        border: 1px solid rgba(56,189,248,0.35);
        background: rgba(15,118,110,0.18);
        color: #38bdf8;
      }}
      h1 {{
        margin: 0.7rem 0 0.35rem;
        font-size: clamp(2rem, 2.25vw, 2.8rem);
        color: #f8fafc;
      }}
      .demo-subtitle {{
        margin: 0;
        max-width: 34rem;
        color: rgba(226,232,240,0.78);
      }}
      .demo-actions {{
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
      }}
      .demo-button {{
        border: 1px solid rgba(56,189,248,0.45);
        background: linear-gradient(120deg, rgba(56,189,248,0.32), rgba(56,189,248,0.16));
        color: #e0f2fe;
        padding: 0.65rem 1.2rem;
        border-radius: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }}
      .demo-button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 16px 36px rgba(56,189,248,0.24);
      }}
      .demo-button--ghost {{
        background: rgba(2,6,23,0.6);
        border: 1px solid rgba(148,163,184,0.38);
        color: rgba(226,232,240,0.85);
      }}
      .demo-nav {{
        margin: 2.35rem 0 1.8rem;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
      }}
      .demo-nav__item {{
        all: unset;
        cursor: pointer;
        padding: 1rem 1.15rem;
        border-radius: 18px;
        border: 1px solid rgba(148,163,184,0.24);
        background: rgba(15,23,42,0.67);
        transition: border-color 0.2s ease, background 0.2s ease, transform 0.18s ease;
        display: grid;
        gap: 0.35rem;
      }}
      .demo-nav__item:hover {{
        border-color: rgba(56,189,248,0.55);
        background: rgba(8,47,73,0.55);
      }}
      .demo-nav__item.is-active {{
        border-color: rgba(56,189,248,0.75);
        background: linear-gradient(135deg, rgba(56,189,248,0.24), rgba(15,23,42,0.82));
        box-shadow: 0 18px 44px rgba(56,189,248,0.22);
        transform: translateY(-2px);
      }}
      .demo-nav__item a {{
        all: unset;
        cursor: pointer;
        display: grid;
        gap: 0.35rem;
      }}
      .demo-nav__label {{
        font-weight: 600;
        color: #f8fafc;
      }}
      .demo-nav__hint {{
        font-size: 0.85rem;
        color: rgba(203,213,225,0.76);
      }}
      .demo-overview {{
        display: flex;
        justify-content: space-between;
        gap: 1.5rem;
        align-items: flex-end;
      }}
      .demo-meta h2 {{
        margin: 0;
        font-size: 1.6rem;
        color: #f8fafc;
      }}
      .demo-meta p {{
        margin: 0.35rem 0 0;
        color: rgba(226,232,240,0.72);
      }}
      .demo-metrics {{
        display: flex;
        gap: 0.65rem;
        flex-wrap: wrap;
      }}
      .demo-metric {{
        font-size: 0.8rem;
        padding: 0.55rem 0.95rem;
        border-radius: 999px;
        background: rgba(15,118,110,0.18);
        border: 1px solid rgba(45,212,191,0.35);
        color: #99f6e4;
        letter-spacing: 0.05em;
      }}
      .demo-error {{
        padding: 2rem;
        text-align: center;
        font-size: 1rem;
        color: rgba(248,113,113,0.85);
      }}
    </style>
  </head>
  <body>
    <main>
      <div class="demo-shell">
        <div class="demo-content">
          <div id="app"></div>
        </div>
      </div>
    </main>
    <script type="module">
      const manifestEndpoint = "{MANIFEST_ENDPOINT}";
      const pageId = "{page_id}";

      async function bootstrap() {{
        const [vue, engineModule] = await Promise.all([
          import("vue"),
          import("/static/layout-engine-vue/index.js"),
        ]);

        const {{ createApp, computed }} = vue;
        const engine = await engineModule.createLayoutEngineApp({{
          manifestUrl: `${{manifestEndpoint}}?page=${{pageId}}`,
        }});

        const App = {{
          name: "LayoutEngineDemoShell",
          components: {{
            LayoutEngineShell: engineModule.LayoutEngineShell,
          }},
          setup() {{
            const manifest = engineModule.useLayoutManifest();
            const site = engineModule.useSiteNavigation(manifest);
            const theme = computed(() => manifest.meta?.theme ?? {{}});
            const pageMeta = computed(() => manifest.meta?.page ?? {{}});
            const navPages = computed(() => site.pages.value);
            const isActive = (targetId) => site.activePage.value?.id === targetId;
            const accentStyle = computed(() => ({{
              "--accent": theme.value?.accent ?? "#38bdf8",
            }}));
            const navClass = (targetId) => ({{
              "is-active": isActive(targetId),
            }});
            return {{
              manifest,
              site,
              theme,
              pageMeta,
              navPages,
              isActive,
              accentStyle,
              navClass,
              title: "{title}",
            }};
          }},
          template: `
            <div class="demo-shell-inner" :style="accentStyle">
              <LayoutEngineShell>
                <template #default>
                  <header class="demo-header">
                    <div>
                      <span class="demo-badge">MPA Demo</span>
                      <h1>{{{{ title }}}}</h1>
                      <p class="demo-subtitle">
                        {{{{ pageMeta.tagline || 'Navigable dashboard shell driven by Layout Engine manifests.' }}}}
                      </p>
                    </div>
                    <div class="demo-actions">
                      <button class="demo-button">Create Report</button>
                      <button class="demo-button demo-button--ghost">Share</button>
                    </div>
                  </header>
                  <nav class="demo-nav">
                    <div
                      v-for="page in navPages"
                      :key="page.id"
                      class="demo-nav__item"
                      :class="navClass(page.id)"
                    >
                      <a :href="page.route">
                        <span class="demo-nav__label">{{{{ page.title ?? page.id }}}}</span>
                        <span class="demo-nav__hint">{{{{ page.meta?.tagline ?? '' }}}}</span>
                      </a>
                    </div>
                  </nav>
                  <section class="demo-overview">
                    <div class="demo-meta">
                      <h2>{{{{ pageMeta.title ?? (site.activePage.value?.title || 'Overview') }}}}</h2>
                      <p>{{{{ pageMeta.description || 'Curated view powered by SwarmaKit atoms and the layout engine.' }}}}</p>
                    </div>
                    <div class="demo-metrics">
                      <div class="demo-metric">Viewport {{{{ manifest.viewport?.width }}}} × {{{{ manifest.viewport?.height }}}}</div>
                      <div class="demo-metric" v-if="manifest.grid?.tokens?.columns">Grid {{{{ manifest.grid.tokens.columns }}}}</div>
                      <div class="demo-metric">Tiles {{{{ manifest.tiles.length }}}}</div>
                    </div>
                  </section>
                </template>
              </LayoutEngineShell>
            </div>
          `,
        }};

        const app = createApp(App);
        app.use(engine.plugin);
        app.mount("#app");
      }}

      bootstrap().catch((error) => {{
        console.error("Dashboard bootstrap failed", error);
        const host = document.getElementById("app");
        if (host) {{
          host.innerHTML = '<p class="demo-error">We could not load the dashboard. Check the server logs.</p>';
        }}
      }});
    </script>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html = _render_shell(title=APP_TITLE, page_id=DEFAULT_PAGE_ID)
    return HTMLResponse(html)


@app.get(MANIFEST_ENDPOINT, response_class=JSONResponse)
async def manifest(page: str | None = Query(default=None)) -> JSONResponse:
    target = page or DEFAULT_PAGE_ID
    try:
        payload = build_manifest(target)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return JSONResponse(content=payload.model_dump())


@app.get("/{path:path}", response_class=HTMLResponse)
async def multipage_router(path: str) -> HTMLResponse:
    if path.startswith("static/") or path == MANIFEST_ENDPOINT.lstrip("/"):
        raise HTTPException(status_code=404, detail="Not found")

    route = f"/{path}" if path else "/"
    page_id = resolve_page_by_route(route) or DEFAULT_PAGE_ID
    html = _render_shell(title=APP_TITLE, page_id=page_id)
    return HTMLResponse(html)


__all__ = ["app"]
