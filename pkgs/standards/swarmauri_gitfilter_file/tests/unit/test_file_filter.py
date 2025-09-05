from swarmauri_gitfilter_file import FileFilter


def test_clean_smudge(tmp_path):
    filt = FileFilter(output_dir=tmp_path)
    oid = filt.clean(b"data")
    assert filt.smudge(oid) == b"data"


def test_resource_type(tmp_path):
    filt = FileFilter(output_dir=tmp_path)
    assert filt.resource == "StorageAdapter"
    assert filt.type == "FileFilter"


def test_round_trip_serialization(tmp_path):
    filt = FileFilter(output_dir=tmp_path)
    data = filt.model_dump()
    restored = FileFilter(output_dir=tmp_path, **data)
    assert restored.type == filt.type
