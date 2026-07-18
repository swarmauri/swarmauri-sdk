"""Tests for Sync Labs lip-sync plugin citizenship."""

import pytest

from swarmauri.interface_registry import InterfaceRegistry
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


pytestmark = pytest.mark.unit


def test_synclabs_lipsync_is_first_class_video_lipsync() -> None:
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.video_lipsync.SyncLabsLipSync"
        ]
        == "swarmauri_video_lipsync_synclabs.SyncLabsLipSync"
    )


def test_video_lipsync_namespace_uses_lipsync_base() -> None:
    assert (
        InterfaceRegistry.INTERFACE_IMPORT_PATHS["swarmauri.video_lipsync"]
        == "swarmauri_base.video_lipsync.LipSyncBase"
    )
