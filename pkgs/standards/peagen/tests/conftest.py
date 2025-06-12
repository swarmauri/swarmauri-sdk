import pytest

try:
    from pytest_socket import disable_socket
except Exception:  # pragma: no cover - optional
    disable_socket = None

try:
    import psutil
except ImportError:  # pragma: no cover - optional
    psutil = None


@pytest.fixture(autouse=True)
def _socket_guard() -> None:
    if disable_socket:
        disable_socket()


@pytest.fixture
def cpu_mem_profile():
    if not psutil:
        pytest.skip("psutil not available")
    proc = psutil.Process()
    before = proc.cpu_times().user
    mem_before = proc.memory_info().rss
    yield
    after = proc.cpu_times().user
    mem_after = proc.memory_info().rss
    print(f"CPU(s): {after - before:.4f}  RSS: {mem_after - mem_before}")
