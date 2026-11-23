"""Tests for the common lip-sync component base."""

from typing import Any, Literal

import pytest
from pydantic import ValidationError

from swarmauri_base.video_lipsync import LipSyncBase


class ExampleLipSync(LipSyncBase):
    allowed_models: list[str] = ["example"]
    name: str = "example"
    type: Literal["ExampleLipSync"] = "ExampleLipSync"

    def predict(
        self,
        video: str,
        audio: str,
        output_path: str = "output.mp4",
        **kwargs: Any,
    ) -> str:
        return output_path

    async def apredict(
        self,
        video: str,
        audio: str,
        output_path: str = "output.mp4",
        **kwargs: Any,
    ) -> str:
        return output_path


def test_base_exposes_video_lip_sync_resource() -> None:
    model = ExampleLipSync()

    assert model.resource == "VideoLipSync"


def test_base_rejects_unknown_model_name() -> None:
    with pytest.raises(
        ValidationError, match="Model name unknown is not allowed"
    ):
        ExampleLipSync(name="unknown")
