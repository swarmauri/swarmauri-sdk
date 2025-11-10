from __future__ import annotations

import asyncio
import random
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request

from layout_engine_atoms.runtime.svelte import (
    SvelteLayoutOptions,
    SvelteRouterOptions,
    SvelteUIHooks,
    mount_svelte_app,
)
from layout_engine_atoms.runtime.vue.realtime import (
    RealtimeBinding,
    RealtimeChannel,
    RealtimeOptions,
    WebsocketMuxHub,
)

from .manifests import DEFAULT_PAGE_ID, build_manifest

app = FastAPI(title="Layout Engine Svelte Demo", docs_url=None)

PULSE_CHANNEL = RealtimeChannel(
    id="svelte.pulse",
    scope="site",
    topic="svelte-demo:pulse",
    description="Updates the hero pulse tile in realtime.",
)


def _manifest_builder(request: Request):
    page_id = request.query_params.get("page") or DEFAULT_PAGE_ID
    try:
        return build_manifest(page_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


async def pulse_publisher(hub: WebsocketMuxHub) -> None:
    messages = [
        "Svelte runtime is fully synced.",
        "Websocket latency holding at 140ms.",
        "Streaming live telemetry events.",
        "Regenerating Svelte manifest tiles.",
    ]
    idx = 0
    while True:
        payload = {
            "message": messages[idx % len(messages)],
            "level": "success" if idx % 2 == 0 else "info",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        idx += 1
        await hub.broadcast(PULSE_CHANNEL.id, payload)
        await asyncio.sleep(random.uniform(3.0, 6.0))


layout_options = SvelteLayoutOptions(
    title="Svelte Layout Engine Dashboard",
    accent_palette={
        "accent": "rgba(248, 113, 113, 0.75)",
        "panel": "rgba(23, 23, 23, 0.92)",
        "surface": "rgba(2, 6, 23, 1)",
        "text": "#f5f5f4",
    },
    router=SvelteRouterOptions(
        manifest_url="./manifest.json",
        page_param="page",
        default_page_id=DEFAULT_PAGE_ID,
    ),
)

ui_hooks = SvelteUIHooks(
    header_slot="""
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <h1 style="margin:0;font-size:2.25rem;">Svelte Runtime</h1>
          <p style="margin:0.5rem 0 0;color:rgba(245,245,244,0.75);">
            Layout Engine dashboard rendered through mount_svelte_app with realtime bindings.
          </p>
        </div>
      </div>
    """,
)

mount_svelte_app(
    app,
    _manifest_builder,
    base_path="/",
    layout_options=layout_options,
    ui_hooks=ui_hooks,
    realtime=RealtimeOptions(
        path="/ws/pulse",
        channels=(PULSE_CHANNEL,),
        publishers=(pulse_publisher,),
        bindings=(
            RealtimeBinding(
                channel=PULSE_CHANNEL.id,
                tile_id="overview_pulse",
                fields={
                    "message": "message",
                    "type": "level",
                    "timestamp": "timestamp",
                },
            ),
        ),
    ),
)
