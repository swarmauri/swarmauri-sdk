import pytest
import fsspec
import s3fs
from swarmauri_program_s3fs import S3fsProgram


class MemoryS3FS(s3fs.S3FileSystem):
    """s3fs filesystem backed by in-memory fsspec store for testing."""

    def __init__(self):
        super().__init__(anon=True)
        self.store = fsspec.filesystem("memory")

    # Delegate required methods to memory fs
    def open(self, path, mode="r", **kwargs):  # type: ignore[override]
        return self.store.open(path, mode, **kwargs)

    def glob(self, path, **kwargs):
        return self.store.glob(path, **kwargs)

    def isdir(self, path):  # type: ignore[override]
        return self.store.isdir(path)

    def exists(self, path):  # type: ignore[override]
        return self.store.exists(path)

    def makedirs(self, path, exist_ok=False):
        self.store.mkdirs(path, exist_ok=exist_ok)


@pytest.fixture
def mem_fs():
    return MemoryS3FS()


@pytest.mark.unit
def test_ubc_resource():
    assert S3fsProgram().resource == "Program"


@pytest.mark.unit
def test_ubc_type():
    assert S3fsProgram().type == "S3fsProgram"


@pytest.mark.unit
def test_serialization():
    prog = S3fsProgram()
    assert prog.id == S3fsProgram.model_validate_json(prog.model_dump_json()).id


@pytest.mark.unit
def test_from_and_save_s3(mem_fs):
    # prepare files in memory fs
    mem_fs.makedirs("bucket/prefix", exist_ok=True)
    with mem_fs.open("bucket/prefix/hello.py", "w") as f:
        f.write("print('hi')")

    prog = S3fsProgram.from_s3(bucket="bucket", prefix="prefix", fs=mem_fs)
    assert prog.content["hello.py"] == "print('hi')"

    prog.content["readme.md"] = "info"
    prog.save_to_s3(bucket="bucket2", prefix="prog",)
    with mem_fs.open("bucket2/prog/readme.md") as f:
        assert f.read() == "info"
