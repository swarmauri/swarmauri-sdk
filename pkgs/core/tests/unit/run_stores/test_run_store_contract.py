from dataclasses import FrozenInstanceError

import pytest

from swarmauri_core.run_stores import IRunStore, RunCheckpoint


def test_checkpoint_is_immutable_and_interface_is_abstract():
    checkpoint = RunCheckpoint("run", 0, "opaque")
    with pytest.raises(FrozenInstanceError):
        checkpoint.revision = 1
    with pytest.raises(TypeError):
        IRunStore()
