from swarmauri_similarity_gzip import GzipSimilarity


def test_gzip_similarity_class_type():
    assert GzipSimilarity.type == "GzipSimilarity"


def test_gzip_similarity_instance_type():
    assert GzipSimilarity().type == "GzipSimilarity"


def test_gzip_similarity_json_roundtrip():
    original = GzipSimilarity(compresslevel=6, symmetric=False)

    restored = GzipSimilarity.model_validate_json(original.model_dump_json())

    assert restored.type == original.type == "GzipSimilarity"
    assert restored.compresslevel == original.compresslevel == 6
    assert restored.symmetric is original.symmetric is False
    assert restored.similarity("alpha", "beta") == original.similarity(
        "alpha", "beta"
    )
