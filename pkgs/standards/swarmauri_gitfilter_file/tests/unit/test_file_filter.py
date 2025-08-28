from swarmauri_gitfilter_file import FileFilter


def test_clean_smudge(tmp_path):
    filt = FileFilter(output_dir=tmp_path)
    oid = filt.clean(b"data")
    assert filt.smudge(oid) == b"data"
