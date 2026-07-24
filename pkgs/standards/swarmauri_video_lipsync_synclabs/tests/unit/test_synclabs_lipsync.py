"""Unit tests for the Sync Labs lip-sync provider."""

from pathlib import Path
from typing import Any

import httpx
import pytest

from swarmauri_core.video_lipsync import IQueuedLipSync
from swarmauri_video_lipsync_synclabs import SyncLabsLipSync


pytestmark = pytest.mark.unit


def _install_sync_clients(
    monkeypatch: pytest.MonkeyPatch,
    api_handler: Any,
    external_handler: Any,
) -> None:
    api_transport = httpx.MockTransport(api_handler)
    external_transport = httpx.MockTransport(external_handler)

    monkeypatch.setattr(
        SyncLabsLipSync,
        "_create_api_client",
        lambda self: httpx.Client(
            base_url=self.base_url,
            headers=self._headers(),
            transport=api_transport,
        ),
    )
    monkeypatch.setattr(
        SyncLabsLipSync,
        "_create_external_client",
        lambda self: httpx.Client(transport=external_transport),
    )


def _install_async_clients(
    monkeypatch: pytest.MonkeyPatch,
    api_handler: Any,
    external_handler: Any,
) -> None:
    api_transport = httpx.MockTransport(api_handler)
    external_transport = httpx.MockTransport(external_handler)

    monkeypatch.setattr(
        SyncLabsLipSync,
        "_create_async_api_client",
        lambda self: httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._headers(),
            transport=api_transport,
        ),
    )
    monkeypatch.setattr(
        SyncLabsLipSync,
        "_create_async_external_client",
        lambda self: httpx.AsyncClient(transport=external_transport),
    )


def test_component_contract_and_secret_serialization() -> None:
    model = SyncLabsLipSync(api_key="secret")

    assert isinstance(model, IQueuedLipSync)
    assert model.resource == "VideoLipSync"
    assert "api_key" not in model.model_dump()
    assert "secret" not in repr(model)


def test_predict_submits_polls_and_downloads_without_leaking_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen_payload: dict[str, Any] = {}

    def api_handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-api-key"] == "secret"
        if request.method == "POST":
            seen_payload.update(__import__("json").loads(request.content))
            return httpx.Response(201, json={"id": "job-1"})
        assert request.url.params["include"] == "progress"
        return httpx.Response(
            200,
            json={
                "id": "job-1",
                "status": "COMPLETED",
                "progress_percent": 100,
                "outputUrl": "https://media.example/result.mp4",
            },
        )

    def external_handler(request: httpx.Request) -> httpx.Response:
        assert "x-api-key" not in request.headers
        return httpx.Response(200, content=b"video-bytes")

    _install_sync_clients(monkeypatch, api_handler, external_handler)
    model = SyncLabsLipSync(api_key="secret", poll_interval=0)
    output = tmp_path / "result.mp4"

    result = model.predict(
        "https://media.example/source.mp4",
        "https://media.example/audio.wav",
        str(output),
        sync_mode="cut_off",
    )

    assert result == str(output.resolve())
    assert output.read_bytes() == b"video-bytes"
    assert seen_payload == {
        "model": "lipsync-2",
        "input": [
            {"type": "video", "url": "https://media.example/source.mp4"},
            {"type": "audio", "url": "https://media.example/audio.wav"},
        ],
        "options": {"sync_mode": "cut_off"},
    }


def test_local_media_uses_asset_upload_without_external_auth(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    video = tmp_path / "speaker.mp4"
    video.write_bytes(b"source-video")
    external_headers: list[httpx.Headers] = []

    def api_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v2/assets/upload":
            return httpx.Response(
                201,
                json={
                    "uploadUrl": "https://upload.example/signed",
                    "url": "https://assets.example/speaker.mp4",
                },
            )
        if request.url.path == "/v2/assets":
            return httpx.Response(201, json={"id": "asset-video"})
        return httpx.Response(201, json={"id": "job-1"})

    def external_handler(request: httpx.Request) -> httpx.Response:
        external_headers.append(request.headers)
        return httpx.Response(200)

    _install_sync_clients(monkeypatch, api_handler, external_handler)
    model = SyncLabsLipSync(api_key="secret")

    assert (
        model.submit(str(video), "https://media.example/audio.wav") == "job-1"
    )
    assert external_headers
    assert all("x-api-key" not in headers for headers in external_headers)


@pytest.mark.asyncio
async def test_apredict_uses_native_async_clients(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def api_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(201, json={"id": "job-async"})
        return httpx.Response(
            200,
            json={
                "id": "job-async",
                "status": "COMPLETED",
                "outputUrl": "https://media.example/async.mp4",
            },
        )

    def external_handler(request: httpx.Request) -> httpx.Response:
        assert "x-api-key" not in request.headers
        return httpx.Response(200, content=b"async-video")

    _install_async_clients(monkeypatch, api_handler, external_handler)
    model = SyncLabsLipSync(api_key="secret", poll_interval=0)
    output = tmp_path / "async.mp4"

    result = await model.apredict(
        "https://media.example/source.mp4",
        "https://media.example/audio.wav",
        str(output),
    )

    assert result == str(output.resolve())
    assert output.read_bytes() == b"async-video"


def test_failed_job_raises_provider_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def api_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(201, json={"id": "job-failed"})
        return httpx.Response(
            200,
            json={
                "id": "job-failed",
                "status": "FAILED",
                "error": "video inaccessible",
                "errorCode": "generation_input_video_inaccessible",
            },
        )

    _install_sync_clients(
        monkeypatch,
        api_handler,
        lambda request: httpx.Response(500),
    )
    model = SyncLabsLipSync(api_key="secret", poll_interval=0)

    with pytest.raises(RuntimeError, match="video inaccessible"):
        model.predict(
            "https://media.example/source.mp4",
            "https://media.example/audio.wav",
        )
