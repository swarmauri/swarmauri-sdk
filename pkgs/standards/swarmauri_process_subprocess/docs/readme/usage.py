from swarmauri_core.processes import ProcessRequest
from swarmauri_process_subprocess import SubprocessBackend

backend = SubprocessBackend()
handle = backend.start(ProcessRequest(("python", "--version")))
cursor = 0
while True:
    page = backend.read(handle, after=cursor, wait=1)
    cursor = page.cursor
    for event in page.events:
        print(event.kind, event.data, event.exit_code)
    if page.events and page.events[-1].kind == "exit":
        break
backend.release(handle)
