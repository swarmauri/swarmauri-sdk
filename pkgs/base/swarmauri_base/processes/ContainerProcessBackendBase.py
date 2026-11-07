import subprocess
from dataclasses import replace
from threading import Lock, Timer
from uuid import uuid4

from swarmauri_core.processes import (
    IProcessBackend,
    ProcessHandle,
    ProcessRequest,
)

# Coordinate launch and cancellation inside the target Linux environment.
# The lock closes the race between publishing the PID and a cancellation.
_LAUNCH = """
import fcntl, os, pathlib, subprocess, sys
root = pathlib.Path('/tmp') / ('swarmauri-' + sys.argv[1])
root.mkdir(mode=0o700, exist_ok=True)
with (root / 'lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    if (root / 'cancel').exists():
        sys.exit(125)
    if sys.argv[2]:
        os.chdir(sys.argv[2])
    process = subprocess.Popen(
        sys.argv[3:], start_new_session=True, stdin=sys.stdin.buffer
    )
    (root / 'pid').write_text(str(process.pid))
status = process.wait()
with (root / 'lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    (root / 'pid').unlink(missing_ok=True)
    (root / 'done').touch()
sys.exit(status if status >= 0 else 128 - status)
"""

_CANCEL = """
import fcntl, os, pathlib, signal, sys
root = pathlib.Path('/tmp') / ('swarmauri-' + sys.argv[1])
root.mkdir(mode=0o700, exist_ok=True)
with (root / 'lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    if (root / 'done').exists():
        print('finished')
        sys.exit(0)
    (root / 'cancel').touch()
    try:
        os.killpg(int((root / 'pid').read_text()), signal.SIGKILL)
    except (FileNotFoundError, ProcessLookupError):
        pass
"""

_CLEAN = """
import pathlib, shutil, sys
root = pathlib.Path('/tmp') / ('swarmauri-' + sys.argv[1])
if root.exists():
    shutil.rmtree(root)
"""


class ContainerProcessBackendBase(IProcessBackend):
    """Share process control across container command transports."""

    def __init__(self, transport: IProcessBackend):
        self.transport = transport
        self._runs = {}
        self._lock = Lock()

    def _exec(self, workspace: str, argv: tuple[str, ...], interactive=False):
        raise NotImplementedError

    @staticmethod
    def _control(argv: tuple[str, ...]) -> str:
        return subprocess.run(
            argv,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout

    def start(self, request: ProcessRequest) -> ProcessHandle:
        if not request.workspace:
            raise ValueError("A container workspace is required")
        token = uuid4().hex
        environment = tuple(
            f"{key}={value}" for key, value in (request.env or {}).items()
        )
        argv = (
            "env",
            "--",
            *environment,
            "python3",
            "-c",
            _LAUNCH,
            token,
            request.cwd or "",
            *request.argv,
        )
        handle = self.transport.start(
            ProcessRequest(
                self._exec(request.workspace, argv, interactive=True),
            )
        )
        timer = None
        if request.timeout is not None:
            timer = Timer(
                request.timeout, self._cancel, args=(handle, "timed_out")
            )
            timer.daemon = True
        with self._lock:
            self._runs[handle.id] = (request.workspace, token, timer, None)
        if timer is not None:
            timer.start()
        return handle

    def read(self, handle, *, after=0, wait=0):
        page = self.transport.read(handle, after=after, wait=wait)
        if page.events and page.events[-1].kind == "exit":
            with self._lock:
                _, _, timer, outcome = self._runs[handle.id]
                if timer is not None:
                    timer.cancel()
            if outcome is not None:
                event = replace(page.events[-1], outcome=outcome)
                return replace(page, events=(*page.events[:-1], event))
        return page

    def write_stdin(self, handle, data, *, close=False):
        self.transport.write_stdin(handle, data, close=close)

    def _cancel(self, handle, outcome):
        with self._lock:
            if handle.id not in self._runs:
                return False
            workspace, token, timer, prior = self._runs[handle.id]
            if prior is not None:
                return False
            response = self._control(
                self._exec(workspace, ("python3", "-c", _CANCEL, token))
            )
            if response.strip() == "finished":
                return False
            self._runs[handle.id] = (workspace, token, timer, outcome)
            return True

    def cancel(self, handle):
        return self._cancel(handle, "cancelled")

    def release(self, handle):
        with self._lock:
            workspace, token, timer, _ = self._runs[handle.id]
            page = self.transport.read(handle)
            if not page.events or page.events[-1].kind != "exit":
                raise ValueError("Release requires a completed process")
            if timer is not None:
                timer.cancel()
            self._control(
                self._exec(workspace, ("python3", "-c", _CLEAN, token))
            )
            self.transport.release(handle)
            del self._runs[handle.id]
