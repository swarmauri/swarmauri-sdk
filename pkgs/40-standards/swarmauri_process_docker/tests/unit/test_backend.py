from unittest.mock import Mock

import pytest
from swarmauri_core.processes import (
    IProcessBackend,
    ProcessEvent,
    ProcessHandle,
    ProcessOutput,
    ProcessRequest,
)
from swarmauri_process_docker import DockerProcessBackend


@pytest.mark.unit
def test_cancel_targets_remote_workspace(monkeypatch):
    transport = Mock(spec=IProcessBackend)
    transport.start.return_value = ProcessHandle("one")
    transport.read.return_value = ProcessOutput()
    backend = DockerProcessBackend(transport=transport)
    control = Mock()
    monkeypatch.setattr(backend, "_control", control)

    handle = backend.start(
        ProcessRequest(("python3", "-V"), workspace="workspace")
    )
    request = transport.start.call_args.args[0]
    prefix = ("docker", "exec", "-i", "--", "workspace")
    assert request.argv[: len(prefix)] == prefix
    assert request.argv[-2:] == ("python3", "-V")

    assert backend.cancel(handle)
    command = control.call_args.args[0]
    assert "workspace" in command
    assert command[-1] == request.argv[-4]
    transport.cancel.assert_not_called()

    transport.read.return_value = ProcessOutput(
        (ProcessEvent(1, "exit", exit_code=137),), 1
    )
    assert backend.read(handle).events[-1].outcome == "cancelled"
    backend.release(handle)
    transport.release.assert_called_once_with(handle)
