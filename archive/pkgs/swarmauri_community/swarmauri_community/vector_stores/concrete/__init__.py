from swarmauri.utils._lazy_import import _lazy_import

vector_store_files = [
    ("swarmauri_community.vector_stores.concrete.AnnoyVectorStore", "AnnoyVectorStore"),
    ("swarmauri_community.vector_stores.concrete.CloudQdrantVectorStore", "CloudQdrantVectorStore"),
    ("swarmauri_community.vector_stores.concrete.CloudWeaviateVectorStore", "CloudWeaviateVectorStore"),
    ("swarmauri_community.vector_stores.concrete.Doc2VecVectorStore", "Doc2VecVectorStore"),
    ("swarmauri_community.vector_stores.concrete.DuckDBVectorStore", "DuckDBVectorStore"),
    ("swarmauri_community.vector_stores.concrete.MlmVectorStore", "MlmVectorStore"),
    ("swarmauri_community.vector_stores.concrete.Neo4jVectorStore", "Neo4jVectorStore"),
    ("swarmauri_community.vector_stores.concrete.PersistentChromaDBVectorStore", "PersistentChromaDBVectorStore"),
    ("swarmauri_community.vector_stores.concrete.PersistentQdrantVectorStore", "PersistentQdrantVectorStore"),
    ("swarmauri_community.vector_stores.concrete.PineconeVectorStore", "PineconeVectorStore"),
    ("swarmauri_community.vector_stores.concrete.RedisVectorStore", "RedisVectorStore"),
]

for module_name, class_name in vector_store_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

__all__ = [class_name for _, class_name in vector_store_files]
