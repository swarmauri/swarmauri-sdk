from swarmauri_core.processes import ProcessRequest
from swarmauri_process_kubernetes import KubernetesProcessBackend

backend = KubernetesProcessBackend()
# The target workspace must already exist and include Python 3.
handle = backend.start(
    ProcessRequest(("python3", "--version"), workspace="sdk-checks")
)
print(backend.read(handle, wait=1))
