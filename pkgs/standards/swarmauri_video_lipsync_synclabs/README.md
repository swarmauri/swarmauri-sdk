![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri Sync Labs Lip Sync

`swarmauri_video_lipsync_synclabs` is the standalone Sync Labs provider for
Swarmauri lip-sync video generation. `SyncLabsLipSync` implements the common
`LipSyncBase` contract and exposes Sync Labs' queued job lifecycle without
misrepresenting progress events as streamed video.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_video_lipsync_synclabs)](https://pepy.tech/projects/swarmauri_video_lipsync_synclabs)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_video_lipsync_synclabs.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_video_lipsync_synclabs/)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_video_lipsync_synclabs/)
[![License](https://img.shields.io/pypi/l/swarmauri_video_lipsync_synclabs)](https://pypi.org/project/swarmauri_video_lipsync_synclabs/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_video_lipsync_synclabs)](https://pypi.org/project/swarmauri_video_lipsync_synclabs/)

## Features

- Common synchronous and asynchronous `predict` workflows.
- Observable queued jobs through `submit`, `get_status`, `iter_events`, and
  `aiter_events`.
- Normalized queued, running, completed, failed, and rejected job events.
- Public URL inputs and local video/audio uploads through Sync Labs assets.
- Preflight cost estimation through Sync Labs' estimate endpoint.
- Retry handling for rate limits and safe transient requests.
- API credentials excluded from serialized component state and external media
  requests.
- Current Sync Labs models: `sync-3`, `lipsync-2`, `lipsync-2-pro`,
  `lipsync-1.9.0-beta`, and `react-1`.

## Installation

```bash
uv add swarmauri_video_lipsync_synclabs
```

```bash
pip install swarmauri_video_lipsync_synclabs
```

Set `SYNC_API_KEY` before submitting billable work.

## Usage

Generate from public media URLs:

```python
import os

from swarmauri_video_lipsync_synclabs import SyncLabsLipSync

lip_sync = SyncLabsLipSync(api_key=os.environ["SYNC_API_KEY"])
result = lip_sync.predict(
    "https://example.com/speaker.mp4",
    "https://example.com/dialogue.wav",
    "dubbed.mp4",
    sync_mode="cut_off",
)
print(result)
```

Local paths are uploaded as reusable Sync Labs assets before generation:

```python
result = lip_sync.predict("speaker.mp4", "dialogue.wav", "dubbed.mp4")
```

Observe a queued job without blocking for the final artifact:

```python
job_id = lip_sync.submit(
    "https://example.com/speaker.mp4",
    "https://example.com/dialogue.wav",
)
for event in lip_sync.iter_events(job_id):
    print(event)
```

These iterators report job progress. Sync Labs returns a completed video
artifact rather than incremental video bytes, so this provider intentionally
does not expose `stream` or `astream`.

## Contributing

This package is part of the
[Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk). Contributions
should follow the repository contribution and style guides.

## License

Apache-2.0
