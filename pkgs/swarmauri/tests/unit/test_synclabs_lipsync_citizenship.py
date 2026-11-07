"""Tests for Sync Labs lip-sync plugin citizenship."""

import pytest

from swarmauri.interface_registry import InterfaceRegistry
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

pytestmark = pytest.mark.unit


def test_synclabs_lipsync_is_second_class_video_lipsync() -> None:
    resource_path = "swarmauri.video_lipsync.SyncLabsLipSync"

    assert (
        PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY[resource_path]
        == "swarmauri_video_lipsync_synclabs.SyncLabsLipSync"
    )
    assert resource_path not in PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY


def test_video_lipsync_namespace_uses_lipsync_base() -> None:
    assert (
        InterfaceRegistry.INTERFACE_IMPORT_PATHS["swarmauri.video_lipsync"]
        == "swarmauri_base.video_lipsync.LipSyncBase"
    )
