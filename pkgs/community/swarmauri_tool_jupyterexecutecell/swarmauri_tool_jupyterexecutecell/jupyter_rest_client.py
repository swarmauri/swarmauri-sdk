"""Jupyter REST client stub for executing code cells."""
from typing import List, Dict, Any
import contextlib
import io
import os
import traceback

try:  # pragma: no cover - optional dependency
    import httpx  # type: ignore
except Exception:  # pragma: no cover - httpx may not be installed
    httpx = None  # type: ignore


def execute_cell(kernel_id: str, code: str) -> List[Dict[str, Any]]:
    """Execute a code cell and return IOPub-style messages.

    If the ``JUPYTER_REST_URL`` environment variable is set and ``httpx`` is
    available, a POST request is sent to that URL using ``httpx``. Otherwise,
    the code is executed locally as a stub so tests can run without a live
    Jupyter server.
    """

    base_url = os.environ.get("JUPYTER_REST_URL")
    if httpx and base_url:
        try:
            with httpx.Client(base_url=base_url, timeout=30) as client:
                response = client.post(f"/api/kernels/{kernel_id}/execute", json={"code": code})
                response.raise_for_status()
                return response.json()  # type: ignore[return-value]
        except Exception as exc:  # pragma: no cover - network errors
            raise RuntimeError(str(exc)) from exc

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    messages: List[Dict[str, Any]] = []
    try:
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            exec(code, {})
    except Exception as exc:  # pragma: no cover - error path tested via tool
        messages.append(
            {
                "msg_type": "error",
                "content": {
                    "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__),
                    "ename": type(exc).__name__,
                    "evalue": str(exc),
                },
            }
        )
    stdout_text = stdout_buffer.getvalue()
    if stdout_text:
        messages.append({"msg_type": "stream", "content": {"name": "stdout", "text": stdout_text}})
    stderr_text = stderr_buffer.getvalue()
    if stderr_text:
        messages.append({"msg_type": "stream", "content": {"name": "stderr", "text": stderr_text}})
    messages.append({"msg_type": "status", "content": {"execution_state": "idle"}})
    return messages
