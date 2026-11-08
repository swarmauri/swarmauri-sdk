import sys

import pytest
from swarmauri_core.processes import ProcessRequest
from swarmauri_process_subprocess import SubprocessBackend

pytestmark = pytest.mark.unit


def collect(backend, handle):
    cursor = 0
    events = []
    for _ in range(10):
        page = backend.read(handle, after=cursor, wait=1)
        cursor = page.cursor
        events.extend(page.events)
        if events and events[-1].kind == "exit":
            backend.release(handle)
            return events
    pytest.fail("No terminal process event")


def test_streams_stdin_stdout_and_stderr():
    backend = SubprocessBackend()
    handle = backend.start(
        ProcessRequest(
            (
                sys.executable,
                "-c",
                "import sys; print(input()); print('stderr', file=sys.stderr)",
            )
        )
    )
    backend.write_stdin(handle, b"hello\n", close=True)
    events = collect(backend, handle)
    assert b"hello" in b"".join(e.data for e in events if e.kind == "stdout")
    assert b"stderr" in b"".join(e.data for e in events if e.kind == "stderr")
    assert events[-1].exit_code == 0


def test_cancellation_terminates_process():
    backend = SubprocessBackend()
    handle = backend.start(
        ProcessRequest(
            (
                sys.executable,
                "-c",
                "import time; time.sleep(60)",
            )
        )
    )
    assert backend.cancel(handle)
    assert collect(backend, handle)[-1].outcome == "cancelled"


def test_timeout_terminates_process():
    backend = SubprocessBackend()
    handle = backend.start(
        ProcessRequest(
            (
                sys.executable,
                "-c",
                "import time; time.sleep(60)",
            ),
            timeout=0.2,
        )
    )
    assert collect(backend, handle)[-1].outcome == "timed_out"
