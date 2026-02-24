from __future__ import annotations

import asyncio
import random
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request

from layout_engine_atoms.runtime.vue.app import (
    LayoutOptions,
    RouterOptions,
    UIHooks,
    mount_layout_app,
)
from layout_engine_atoms.runtime.vue.realtime import (
    RealtimeBinding,
    RealtimeChannel,
    RealtimeOptions,
    WebsocketMuxHub,
)

from .manifests import DEFAULT_PAGE_ID, build_manifest

APP_TITLE = "Swarmauri Mission Control"

app = FastAPI(title="Layout Engine MPA Demo", docs_url=None)

MISSION_EVENTS_CHANNEL = RealtimeChannel(
    id="mission.events",
    scope="site",
    topic="mission-control:events",
    description="Broadcasts live mission control pulses rendered in the overview banner.",
    meta={"demo": True},
)


def _manifest_builder(request: Request):
    page_id = request.query_params.get("page")
    resolved = page_id or DEFAULT_PAGE_ID
    try:
        return build_manifest(resolved)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


async def mission_pulse_publisher(hub: WebsocketMuxHub) -> None:
    """Emit rotating mission control pulses to demonstrate realtime updates."""

    messages = [
        ("success", "Telemetry lock acquired — mission feed is nominal."),
        ("warning", "Playbook 211 stalled for 3m — monitoring escalation lane."),
        ("info", "New insight cards generated from overnight batch windows."),
        ("success", "Realtime mux synced: 3.2k events/min with 120ms p99."),
    ]
    idx = 0
    while True:
        level, message = messages[idx % len(messages)]
        idx += 1
        payload = {
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await hub.broadcast(MISSION_EVENTS_CHANNEL.id, payload)
        await asyncio.sleep(random.uniform(4.0, 7.0))


EXTRA_STYLES = [
    """
<style>
  .le-shell-app {
    position: relative;
  }
  .le-shell__header {
    display: flex;
    justify-content: space-between;
    gap: 1.5rem;
    align-items: flex-start;
    margin-bottom: 2rem;
  }
  .le-shell__badge {
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
  }
  .le-shell__title {
    margin: 0.75rem 0 0.25rem;
    font-size: clamp(2rem, 2.25vw, 2.8rem);
    color: var(--le-text);
  }
  .le-shell__subtitle {
    margin: 0;
    max-width: 34rem;
    color: rgba(226,232,240,0.72);
  }
  .le-shell__actions {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
  .le-shell__button {
    border: 1px solid rgba(56,189,248,0.45);
    background: linear-gradient(120deg, rgba(56,189,248,0.32), rgba(56,189,248,0.16));
    color: #e0f2fe;
    padding: 0.65rem 1.2rem;
    border-radius: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .le-shell__button:hover {
    transform: translateY(-1px);
    box-shadow: 0 16px 36px rgba(56,189,248,0.24);
  }
  .le-shell__button--ghost {
    background: rgba(2,6,23,0.6);
    border: 1px solid rgba(148,163,184,0.38);
    color: rgba(226,232,240,0.85);
  }
  .demo-overview {
    display: flex;
    justify-content: space-between;
    gap: 1.5rem;
    align-items: flex-end;
    margin-bottom: 1.75rem;
  }
  .demo-overview h2 {
    margin: 0;
    font-size: 1.55rem;
    color: var(--le-text);
  }
  .demo-overview p {
    margin: 0.35rem 0 0;
    color: rgba(226,232,240,0.75);
    max-width: 32rem;
  }
  .demo-metrics {
    display: flex;
    gap: 0.65rem;
    flex-wrap: wrap;
  }
  .demo-metric {
    font-size: 0.8rem;
    padding: 0.55rem 0.95rem;
    border-radius: 999px;
    background: rgba(15,118,110,0.18);
    border: 1px solid rgba(45,212,191,0.35);
    color: #99f6e4;
    letter-spacing: 0.05em;
  }
  .demo-nav {
    margin: 1.8rem 0 1.5rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
  }
  .demo-nav__item {
    all: unset;
    cursor: pointer;
    padding: 1rem 1.15rem;
    border-radius: 18px;
    border: 1px solid rgba(148,163,184,0.24);
    background: rgba(15,23,42,0.67);
    transition: border-color 0.2s ease, background 0.2s ease, transform 0.18s ease;
    display: grid;
    gap: 0.35rem;
  }
  .demo-nav__item:hover {
    border-color: rgba(56,189,248,0.55);
    background: rgba(8,47,73,0.55);
  }
  .demo-nav__item.is-active {
    border-color: rgba(56,189,248,0.75);
    background: linear-gradient(135deg, rgba(56,189,248,0.24), rgba(15,23,42,0.82));
    box-shadow: 0 18px 44px rgba(56,189,248,0.22);
    transform: translateY(-2px);
  }
  .demo-nav__label {
    font-weight: 600;
    color: var(--le-text);
  }
  .demo-nav__hint {
    font-size: 0.85rem;
    color: rgba(203,213,225,0.76);
  }
</style>
""",
]

HEADER_SLOT = """
  <div>
    <span class="le-shell__badge">Mission Control</span>
    <h1 class="le-shell__title">{{ shellTitle }}</h1>
    <p v-if="shellSubtitle" class="le-shell__subtitle">{{ shellSubtitle }}</p>
  </div>
  <div class="le-shell__actions">
    <button class="le-shell__button">Create Report</button>
    <button class="le-shell__button le-shell__button--ghost">Share</button>
  </div>
"""

layout_options = LayoutOptions(
    title=APP_TITLE,
    accent_palette={
        "accent": "rgba(56, 189, 248, 0.75)",
        "panel": "rgba(15, 23, 42, 0.92)",
        "surface": "rgba(2, 6, 23, 1)",
        "text": "#e2e8f0",
    },
    extra_styles=EXTRA_STYLES,
    router=RouterOptions(
        manifest_url="./manifest.json",
        page_param="page",
        default_page_id=DEFAULT_PAGE_ID,
        history="history",
        hydrate_site_meta=True,
    ),
)

ui_hooks = UIHooks(
    header_slot=HEADER_SLOT,
    content_slot="""
      <div class="demo-overview">
        <div class="demo-meta">
          <h2>{{ manifest.meta?.page?.title ?? site.activePage.value?.title ?? 'Overview' }}</h2>
          <p>
            {{ manifest.meta?.page?.description ??
               manifest.meta?.page?.tagline ??
               'Curated view powered by SwarmaKit atoms and the layout engine.' }}
          </p>
        </div>
        <div class="demo-metrics" v-if="manifest.viewport">
          <span class="demo-metric">
            Viewport {{ manifest.viewport.width }} × {{ manifest.viewport.height }}
          </span>
          <span class="demo-metric">
            Tiles {{ manifest.tiles.length }}
          </span>
        </div>
      </div>
      <LayoutEngineShell>
        <template #default="{ site }">
          <nav v-if="site.pages.value.length" class="demo-nav">
            <button
              v-for="page in site.pages.value"
              :key="page.id"
              type="button"
              class="demo-nav__item"
              :class="{ 'is-active': page.id === site.activePage.value?.id }"
              @click="handleNavigate(page.id)"
            >
              <span class="demo-nav__label">{{ page.title ?? page.id }}</span>
              <span v-if="page.meta?.tagline" class="demo-nav__hint">{{ page.meta.tagline }}</span>
            </button>
          </nav>
        </template>
      </LayoutEngineShell>
    """,
)

mount_layout_app(
    app,
    _manifest_builder,
    base_path="/",
    layout_options=layout_options,
    ui_hooks=ui_hooks,
    realtime=RealtimeOptions(
        path="/ws/events",
        channels=(MISSION_EVENTS_CHANNEL,),
        publishers=(mission_pulse_publisher,),
        bindings=(
            RealtimeBinding(
                channel=MISSION_EVENTS_CHANNEL.id,
                tile_id="overview_pulses",
                fields={
                    "message": "message",
                    "type": "level",
                    "timestamp": "timestamp",
                },
            ),
        ),
    ),
)
