from swarmauri_core.processes import (
    IProcessBackend,
    ProcessEvent,
    ProcessRequest,
)


def collect_process(
    backend: IProcessBackend,
    request: ProcessRequest,
    data: bytes = b"",
) -> tuple[bytes, bytes, ProcessEvent]:
    """Collect a process result for synchronous tool adapters."""
    handle = backend.start(request)
    stdout, stderr = bytearray(), bytearray()
    cursor = 0
    finished = False
    try:
        backend.write_stdin(handle, data, close=True)
        while True:
            page = backend.read(handle, after=cursor, wait=1)
            cursor = page.cursor
            if page.truncated:
                raise RuntimeError(
                    "Process output exceeded the retained buffer"
                )
            for event in page.events:
                if event.kind == "exit":
                    finished = True
                    return bytes(stdout), bytes(stderr), event
                (stdout if event.kind == "stdout" else stderr).extend(
                    event.data
                )
    finally:
        if not finished:
            backend.cancel(handle)
            while True:
                page = backend.read(handle, after=cursor, wait=1)
                cursor = page.cursor
                if page.events and page.events[-1].kind == "exit":
                    break
        backend.release(handle)
