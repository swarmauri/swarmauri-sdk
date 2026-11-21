from swarmauri_similarity_gzip import GzipSimilarity

similarity = GzipSimilarity()

score = similarity.similarity(
    "The quick brown fox",
    "Le renard brun rapide",
)

ncd = similarity.ncd(
    "The quick brown fox",
    "Le renard brun rapide",
)
