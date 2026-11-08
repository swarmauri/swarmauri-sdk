import os
import subprocess
import threading
from collections import deque
from typing import BinaryIO
from uuid import uuid4

from swarmauri_base.processes._subprocess import (
    _windows_executable,
    run_subprocess,
)
from swarmauri_core.processes import (
    IProcessBackend,
    ProcessEvent,
    ProcessHandle,
    ProcessOutput,
    ProcessRequest,
)


class _Session:
    def __init__(self, process: subprocess.Popen, capacity: int):
        self.process = process
        self.events = deque(maxlen=capacity)
        self.sequence = 0
        self.condition = threading.Condition()
        self.stdin_lock = threading.Lock()
        self.outcome = "exited"
        self.timer = None
        self.done = False

    def publish(self, kind, **fields):
        with self.condition:
            self.sequence += 1
            self.events.append(ProcessEvent(self.sequence, kind, **fields))
            if kind == "exit":
                self.done = True
            self.condition.notify_all()


class SubprocessBackend(IProcessBackend):
    """Run local commands and retain a bounded window of their output."""

    run = staticmethod(run_subprocess)

    def __init__(self, *, output_chunks: int = 256):
        if output_chunks < 1:
            raise ValueError("output_chunks must be positive")
        self.output_chunks = output_chunks
        self._sessions: dict[str, _Session] = {}
        self._lock = threading.Lock()

    def start(self, request: ProcessRequest) -> ProcessHandle:
        if request.workspace is not None:
            raise ValueError("Host processes use cwd to select a workspace")
        executable = (
            _windows_executable(request.argv[0]) if os.name == "nt" else None
        )
        process = subprocess.Popen(
            request.argv,
            executable=executable,
            cwd=request.cwd,
            env=request.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        session = _Session(process, self.output_chunks)
        handle = ProcessHandle(str(uuid4()))
        with self._lock:
            self._sessions[handle.id] = session
        readers = [
            threading.Thread(
                target=self._read_pipe, args=(session, kind, pipe), daemon=True
            )
            for kind, pipe in (
                ("stdout", process.stdout),
                ("stderr", process.stderr),
            )
        ]
        for reader in readers:
            reader.start()
        if request.timeout is not None:
            session.timer = threading.Timer(
                request.timeout,
                self._stop,
                args=(session, "timed_out"),
            )
            session.timer.daemon = True
            session.timer.start()
        threading.Thread(
            target=self._finish, args=(session, readers), daemon=True
        ).start()
        return handle

    @staticmethod
    def _read_pipe(session: _Session, kind: str, pipe: BinaryIO):
        with pipe:
            while data := pipe.read1(4096):
                session.publish(kind, data=data)

    @staticmethod
    def _finish(session: _Session, readers):
        code = session.process.wait()
        if session.timer is not None:
            session.timer.cancel()
        for reader in readers:
            reader.join()
        with session.stdin_lock:
            session.process.stdin.close()
        with session.condition:
            session.publish("exit", exit_code=code, outcome=session.outcome)

    def _session(self, handle):
        with self._lock:
            return self._sessions[handle.id]

    def read(self, handle, *, after=0, wait=0):
        if after < 0 or wait < 0:
            raise ValueError("Cursor and wait must be nonnegative")
        session = self._session(handle)
        with session.condition:
            session.condition.wait_for(
                lambda: session.sequence > after or session.done,
                timeout=wait,
            )
            events = tuple(
                event for event in session.events if event.sequence > after
            )
            return ProcessOutput(
                events,
                events[-1].sequence if events else after,
                bool(events and events[0].sequence > after + 1),
            )

    def write_stdin(self, handle, data, *, close=False):
        session = self._session(handle)
        with session.stdin_lock:
            pipe = session.process.stdin
            if pipe.closed:
                if close and not data:
                    return
                raise ValueError("Process stdin is closed")
            if data:
                pipe.write(data)
                pipe.flush()
            if close:
                pipe.close()

    @staticmethod
    def _stop(session, outcome):
        with session.condition:
            if session.process.poll() is not None:
                return False
            session.outcome = outcome
            session.process.kill()
            return True

    def cancel(self, handle):
        return self._stop(self._session(handle), "cancelled")

    def release(self, handle):
        with self._lock:
            session = self._sessions[handle.id]
            if not session.done:
                raise ValueError("Release requires a completed process")
            del self._sessions[handle.id]
