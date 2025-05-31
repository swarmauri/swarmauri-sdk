import pytest

from swarmauri_program_memorys3fs import MemoryS3FSProgram


@pytest.mark.unit
def test_ubc_resource():
    assert MemoryS3FSProgram().resource == "Program"


@pytest.mark.unit
def test_ubc_type():
    assert MemoryS3FSProgram().type == "MemoryS3FSProgram"


@pytest.mark.unit
def test_serialization():
    prog = MemoryS3FSProgram()
    assert prog.id == MemoryS3FSProgram.model_validate_json(prog.model_dump_json()).id


@pytest.mark.unit
def test_from_and_save_s3():
    # create initial files in memory fs via program instance
    prog = MemoryS3FSProgram()
    prog._fs.makedirs("bucket/prefix", exist_ok=True)
    with prog._fs.open("bucket/prefix/hello.py", "w") as f:
        f.write("print('hi')")

    loaded = MemoryS3FSProgram.from_s3(bucket="bucket", prefix="prefix", fs=prog._fs)
    assert loaded.content["hello.py"] == "print('hi')"

    loaded.content["readme.md"] = "info"
    loaded.save_to_s3(bucket="bucket2", prefix="prog")
    with prog._fs.open("bucket2/prog/readme.md") as f:
        assert f.read() == "info"

