from __future__ import annotations
# Default atoms (role -> ESM module/export/defaults). Consumers can override at call-sites.
DEFAULT_ATOMS = {
    "text":   {"module": "@le/atoms/Text.svelte",   "export": "default", "defaults": {"variant": "body"}},
    "button": {"module": "@le/atoms/Button.svelte", "export": "default", "defaults": {"kind": "primary"}},
    "timeseries": {"module": "@le/atoms/Timeseries.svelte", "export":"default", "defaults":{"legend": True}},
}
