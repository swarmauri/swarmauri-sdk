from swarmauri_similarity_gzip import GzipSimilarity


def test_gzip_similarity_class_type():
    assert GzipSimilarity.type == "GzipSimilarity"


def test_gzip_similarity_instance_type():
    assert GzipSimilarity().type == "GzipSimilarity"
