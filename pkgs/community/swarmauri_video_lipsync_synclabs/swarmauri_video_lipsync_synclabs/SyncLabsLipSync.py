"""Sync Labs lip-sync provider implementation."""

import asyncio
import mimetypes
import time
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any, Literal, cast
from urllib.parse import urlparse

import httpx
from pydantic import Field, SecretStr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.video_lipsync.LipSyncBase import LipSyncBase
from swarmauri_core.video_lipsync.IQueuedLipSync import IQueuedLipSync
from swarmauri_core.video_lipsync.types import (
    LipSyncJobEvent,
    LipSyncJobStatus,
)

_TERMINAL_STATUSES = {"COMPLETED", "FAILED", "REJECTED"}
_STATUS_MAP: dict[str, LipSyncJobStatus] = {
    "PENDING": "QUEUED",
    "PROCESSING": "RUNNING",
    "COMPLETED": "COMPLETED",
    "FAILED": "FAILED",
    "REJECTED": "REJECTED",
}


@ComponentBase.register_type(LipSyncBase, "SyncLabsLipSync")
class SyncLabsLipSync(LipSyncBase, IQueuedLipSync):
    """Generate lip-synced videos with Sync Labs' queued API."""

    allowed_models: list[str] = [
        "sync-3",
        "lipsync-2",
        "lipsync-2-pro",
        "lipsync-1.9.0-beta",
        "react-1",
    ]
    api_key: SecretStr = Field(exclude=True, repr=False)
    name: str = "lipsync-2"
    type: Literal["SyncLabsLipSync"] = "SyncLabsLipSync"
    base_url: str = "https://api.sync.so"
    request_timeout: float = 60.0
    poll_interval: float = 2.0
    max_wait_time: float = 1800.0
    max_retries: int = 3

    def _headers(self) -> dict[str, str]:
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": self.api_key.get_secret_value(),
        }

    def _create_api_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            headers=self._headers(),
            timeout=self.request_timeout,
        )

    def _create_external_client(self) -> httpx.Client:
        return httpx.Client(timeout=self.request_timeout)

    def _create_async_api_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._headers(),
            timeout=self.request_timeout,
        )

    def _create_async_external_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self.request_timeout)

    @staticmethod
    def _is_url(value: str) -> bool:
        return urlparse(value).scheme in {"http", "https"}

    @staticmethod
    def _retry_delay(response: httpx.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass
        return min(2**attempt, 8)

    def _request(
        self,
        client: httpx.Client,
        method: str,
        url: str,
        *,
        retry_server_errors: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            response = client.request(method, url, **kwargs)
            retryable = response.status_code == 429 or (
                retry_server_errors
                and response.status_code in {500, 502, 503, 504}
            )
            if not retryable or attempt == self.max_retries:
                response.raise_for_status()
                return response
            time.sleep(self._retry_delay(response, attempt))
        raise RuntimeError("unreachable retry state")

    async def _arequest(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        *,
        retry_server_errors: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            response = await client.request(method, url, **kwargs)
            retryable = response.status_code == 429 or (
                retry_server_errors
                and response.status_code in {500, 502, 503, 504}
            )
            if not retryable or attempt == self.max_retries:
                response.raise_for_status()
                return response
            await asyncio.sleep(self._retry_delay(response, attempt))
        raise RuntimeError("unreachable retry state")

    def _upload_local_asset(self, path_value: str, asset_type: str) -> str:
        path = Path(path_value).expanduser().resolve(strict=True)
        content_type = mimetypes.guess_type(path.name)[0]
        if content_type is None:
            content_type = (
                "video/mp4" if asset_type == "VIDEO" else "audio/mpeg"
            )

        with self._create_api_client() as api_client:
            upload = self._request(
                api_client,
                "POST",
                "/v2/assets/upload",
                json={
                    "fileName": path.name,
                    "contentType": content_type,
                    "size": path.stat().st_size,
                },
            ).json()

        with (
            path.open("rb") as media,
            self._create_external_client() as external,
        ):
            response = external.put(
                upload["uploadUrl"],
                content=media,
                headers={"Content-Type": content_type},
            )
            response.raise_for_status()

        with self._create_api_client() as api_client:
            asset = self._request(
                api_client,
                "POST",
                "/v2/assets",
                json={
                    "url": upload["url"],
                    "type": asset_type,
                    "name": path.name,
                },
            ).json()
        return cast(str, asset["id"])

    async def _aupload_local_asset(
        self, path_value: str, asset_type: str
    ) -> str:
        path = Path(path_value).expanduser().resolve(strict=True)
        content_type = mimetypes.guess_type(path.name)[0]
        if content_type is None:
            content_type = (
                "video/mp4" if asset_type == "VIDEO" else "audio/mpeg"
            )
        size = path.stat().st_size

        async with self._create_async_api_client() as api_client:
            upload = (
                await self._arequest(
                    api_client,
                    "POST",
                    "/v2/assets/upload",
                    json={
                        "fileName": path.name,
                        "contentType": content_type,
                        "size": size,
                    },
                )
            ).json()

        async def chunks() -> AsyncIterator[bytes]:
            with path.open("rb") as media:
                while chunk := await asyncio.to_thread(
                    media.read, 1024 * 1024
                ):
                    yield chunk

        async with self._create_async_external_client() as external:
            response = await external.put(
                upload["uploadUrl"],
                content=chunks(),
                headers={"Content-Type": content_type},
            )
            response.raise_for_status()

        async with self._create_async_api_client() as api_client:
            asset = (
                await self._arequest(
                    api_client,
                    "POST",
                    "/v2/assets",
                    json={
                        "url": upload["url"],
                        "type": asset_type,
                        "name": path.name,
                    },
                )
            ).json()
        return cast(str, asset["id"])

    def _input(self, value: str, media_type: str) -> dict[str, str]:
        if self._is_url(value):
            return {"type": media_type.lower(), "url": value}
        asset_id = self._upload_local_asset(value, media_type)
        return {"type": media_type.lower(), "assetId": asset_id}

    async def _ainput(self, value: str, media_type: str) -> dict[str, str]:
        if self._is_url(value):
            return {"type": media_type.lower(), "url": value}
        asset_id = await self._aupload_local_asset(value, media_type)
        return {"type": media_type.lower(), "assetId": asset_id}

    def _payload(
        self,
        video_input: dict[str, str],
        audio_input: dict[str, str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        options = dict(kwargs.pop("options", {}))
        for key in tuple(kwargs):
            if key not in {"webhook_url", "output_file_name", "project_id"}:
                options[key] = kwargs.pop(key)

        payload: dict[str, Any] = {
            "model": self.name,
            "input": [video_input, audio_input],
        }
        if options:
            payload["options"] = options
        aliases = {
            "webhook_url": "webhookUrl",
            "output_file_name": "outputFileName",
            "project_id": "projectId",
        }
        for source, target in aliases.items():
            value = kwargs.get(source)
            if value is not None:
                payload[target] = value
        return payload

    def submit(self, video: str, audio: str, **kwargs: Any) -> str:
        """Submit URL or local-file media to Sync Labs."""
        payload = self._payload(
            self._input(video, "VIDEO"),
            self._input(audio, "AUDIO"),
            **kwargs,
        )
        with self._create_api_client() as client:
            response = self._request(
                client,
                "POST",
                "/v2/generate",
                retry_server_errors=False,
                json=payload,
            )
        return cast(str, response.json()["id"])

    async def _asubmit(self, video: str, audio: str, **kwargs: Any) -> str:
        video_input, audio_input = await asyncio.gather(
            self._ainput(video, "VIDEO"),
            self._ainput(audio, "AUDIO"),
        )
        payload = self._payload(video_input, audio_input, **kwargs)
        async with self._create_async_api_client() as client:
            response = await self._arequest(
                client,
                "POST",
                "/v2/generate",
                retry_server_errors=False,
                json=payload,
            )
        return cast(str, response.json()["id"])

    @staticmethod
    def _event(generation: dict[str, Any]) -> LipSyncJobEvent:
        provider_status = str(generation["status"])
        if provider_status not in _STATUS_MAP:
            raise ValueError(f"Unknown Sync Labs status: {provider_status}")
        event = LipSyncJobEvent(
            job_id=str(generation["id"]),
            status=_STATUS_MAP[provider_status],
        )
        progress = generation.get("progress_percent")
        if progress is not None:
            event["progress"] = float(progress) / 100.0
        if generation.get("error"):
            event["message"] = str(generation["error"])
        if generation.get("errorCode"):
            event["error_code"] = str(generation["errorCode"])
        if generation.get("outputUrl"):
            event["output_url"] = str(generation["outputUrl"])
        return event

    def get_status(self, job_id: str) -> LipSyncJobEvent:
        """Fetch and normalize the current Sync Labs generation state."""
        with self._create_api_client() as client:
            response = self._request(
                client,
                "GET",
                f"/v2/generate/{job_id}",
                params={"include": "progress"},
            )
        return self._event(response.json())

    async def _aget_status(self, job_id: str) -> LipSyncJobEvent:
        async with self._create_async_api_client() as client:
            response = await self._arequest(
                client,
                "GET",
                f"/v2/generate/{job_id}",
                params={"include": "progress"},
            )
        return self._event(response.json())

    def iter_events(self, job_id: str) -> Iterator[LipSyncJobEvent]:
        """Poll and yield only changed normalized job states."""
        started = time.monotonic()
        previous: LipSyncJobEvent | None = None
        while time.monotonic() - started <= self.max_wait_time:
            event = self.get_status(job_id)
            if event != previous:
                yield event
                previous = event
            if event["status"] in _TERMINAL_STATUSES:
                return
            time.sleep(self.poll_interval)
        raise TimeoutError(f"Sync Labs job {job_id} did not finish in time")

    async def aiter_events(
        self, job_id: str
    ) -> AsyncIterator[LipSyncJobEvent]:
        """Asynchronously poll and yield only changed normalized states."""
        loop = asyncio.get_running_loop()
        started = loop.time()
        previous: LipSyncJobEvent | None = None
        while loop.time() - started <= self.max_wait_time:
            event = await self._aget_status(job_id)
            if event != previous:
                yield event
                previous = event
            if event["status"] in _TERMINAL_STATUSES:
                return
            await asyncio.sleep(self.poll_interval)
        raise TimeoutError(f"Sync Labs job {job_id} did not finish in time")

    @staticmethod
    def _completed_output(event: LipSyncJobEvent) -> str:
        if event["status"] != "COMPLETED":
            message = event.get(
                "message", "provider returned no error message"
            )
            raise RuntimeError(
                f"Lip-sync job ended with {event['status']}: {message}"
            )
        output_url = event.get("output_url")
        if not output_url:
            raise RuntimeError("Completed lip-sync job returned no output URL")
        return output_url

    def _download(self, output_url: str, output_path: str) -> str:
        path = Path(output_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._create_external_client() as client:
            with client.stream("GET", output_url) as response:
                response.raise_for_status()
                with path.open("wb") as output:
                    for chunk in response.iter_bytes():
                        output.write(chunk)
        return str(path)

    async def _adownload(self, output_url: str, output_path: str) -> str:
        path = Path(output_path).expanduser().resolve()
        await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
        async with self._create_async_external_client() as client:
            async with client.stream("GET", output_url) as response:
                response.raise_for_status()
                with path.open("wb") as output:
                    async for chunk in response.aiter_bytes():
                        await asyncio.to_thread(output.write, chunk)
        return str(path)

    def predict(
        self,
        video: str,
        audio: str,
        output_path: str = "output.mp4",
        **kwargs: Any,
    ) -> str:
        """Submit, await, and download a lip-synced video."""
        job_id = self.submit(video, audio, **kwargs)
        final_event: LipSyncJobEvent | None = None
        for final_event in self.iter_events(job_id):
            pass
        if final_event is None:
            raise RuntimeError(f"Sync Labs job {job_id} returned no state")
        return self._download(
            self._completed_output(final_event),
            output_path,
        )

    async def apredict(
        self,
        video: str,
        audio: str,
        output_path: str = "output.mp4",
        **kwargs: Any,
    ) -> str:
        """Asynchronously submit, await, and download a lip-synced video."""
        job_id = await self._asubmit(video, audio, **kwargs)
        final_event: LipSyncJobEvent | None = None
        async for final_event in self.aiter_events(job_id):
            pass
        if final_event is None:
            raise RuntimeError(f"Sync Labs job {job_id} returned no state")
        return await self._adownload(
            self._completed_output(final_event),
            output_path,
        )

    def estimate_cost(self, video: str, audio: str, **kwargs: Any) -> float:
        """Return the summed estimated generation cost in US dollars."""
        payload = self._payload(
            self._input(video, "VIDEO"),
            self._input(audio, "AUDIO"),
            **kwargs,
        )
        with self._create_api_client() as client:
            estimates = self._request(
                client,
                "POST",
                "/v2/generations/estimate",
                json=payload,
            ).json()
        if isinstance(estimates, dict):
            estimates = [estimates]
        return sum(
            float(
                estimate.get(
                    "estimatedGenerationCost",
                    estimate.get("totalCost", 0.0),
                )
            )
            for estimate in estimates
        )
