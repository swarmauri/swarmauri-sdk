from peagen.result_backends.fs_backend import FSBackend
from peagen.queue.model import Result


def test_fsbackend_persist(tmp_path):
    backend = FSBackend(root=tmp_path)
    res = Result(task_id="42", status="ok", data={})
    backend.save(res)
    got = backend.get("42")
    assert got is not None
    assert got.task_id == "42"
