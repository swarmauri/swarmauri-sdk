import json
import duckdb
import numpy as np
import os
from typing import List, Union, Literal, Dict, Any, Optional
from pydantic import BaseModel, Field

from swarmauri.documents.concrete.Document import Document
from swarmauri.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding
from swarmauri.distances.concrete.CosineDistance import CosineDistance
from swarmauri.vectors.concrete.Vector import Vector

from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import (
    VectorStoreSaveLoadMixin,
)


class DuckDBVectorStore(
    VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase, BaseModel
):
    type: Literal["DuckDBVectorStore"] = "DuckDBVectorStore"
    db_path: str
    vector_size: int
    metric: str
    client: Optional[duckdb.DuckDBPyConnection] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self, db_path: str, vector_size: int, metric: str = "cosine", **kwargs
    ):
        super().__init__(
            db_path=db_path, vector_size=vector_size, metric=metric, **kwargs
        )
        self.db_path = db_path
        self.vector_size = vector_size
        self.metric = metric
        self._embedder = Doc2VecEmbedding(vector_size=self.vector_size)
        self._distance = CosineDistance()
        self.client = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize the database with the VSS extension and create necessary tables."""
        try:
            # Always use in-memory connection for HNSW index
            self.client = duckdb.connect(":memory:")

            # Install and load the VSS extension
            self.client.execute("INSTALL vss")
            self.client.execute("LOAD vss")

            # Create the documents table
            self.client.execute(
                f"""
                CREATE TABLE IF NOT EXISTS documents (
                    id VARCHAR PRIMARY KEY,
                    content TEXT,
                    metadata JSON,
                    embedding FLOAT[{self.vector_size}]
                )
            """
            )

            # Create HNSW index
            self.client.execute(
                f"""
                CREATE INDEX IF NOT EXISTS hnsw_idx
                ON documents
                USING HNSW (embedding)
                WITH (metric = '{self.metric}')
            """
            )

            # If using a file-based path, load existing data into memory
            if self.db_path != ":memory:" and os.path.exists(self.db_path):
                disk_conn = duckdb.connect(self.db_path)
                existing_data = disk_conn.execute("SELECT * FROM documents").fetchall()
                if existing_data:
                    self.client.executemany(
                        """
                        INSERT INTO documents (id, content, metadata, embedding)
                        VALUES (?, ?, ?, ?)
                        """,
                        existing_data,
                    )
                disk_conn.close()

        except Exception as e:
            raise RuntimeError(f"Failed to initialize DuckDB with VSS: {str(e)}")

    def _prepare_vector(self, document: Document) -> Vector:
        """Prepare a vector for insertion into the DuckDB store."""
        if not document.embedding:
            self._embedder.fit([document.content])
            embedding = Vector(value=self._embedder.transform([document.content])[0])
            document.embedding = embedding
        return document.embedding

    def _persist_to_disk(self):
        """Persist in-memory data to disk if using file-based storage."""
        if self.db_path != ":memory:":
            disk_conn = duckdb.connect(self.db_path)
            disk_conn.execute("DROP TABLE IF EXISTS documents")
            self.client.sql("SELECT * FROM documents").to_df().to_sql(
                "documents", disk_conn
            )
            disk_conn.close()

    def add_document(self, document: Document) -> None:
        """Add a single document to the DuckDB store."""
        try:
            embedding = self._prepare_vector(document)
            embedding_list = (
                embedding.value.tolist()
                if isinstance(embedding.value, np.ndarray)
                else embedding.value
            )

            self.client.execute(
                """
                INSERT INTO documents (id, content, metadata, embedding)
                VALUES (?, ?, ?, ?)
                """,
                (
                    document.id,
                    document.content,
                    json.dumps(document.metadata),
                    embedding_list,
                ),
            )

            self._persist_to_disk()
        except Exception as e:
            raise RuntimeError(f"Failed to add document {document.id}: {str(e)}")

    def add_documents(self, documents: List[Document], batch_size: int = 1000) -> None:
        """Add multiple documents to the DuckDB store in batches."""
        try:
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]
                data = [
                    (
                        d.id,
                        d.content,
                        json.dumps(d.metadata),
                        self._prepare_vector(d).value,
                    )
                    for d in batch
                ]
                self.client.executemany(
                    """
                    INSERT INTO documents (id, content, metadata, embedding)
                    VALUES (?, ?, ?, ?)
                    """,
                    data,
                )

            self._persist_to_disk()
        except Exception as e:
            raise RuntimeError(f"Failed to add documents in batch: {str(e)}")

    def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by its ID."""
        try:
            result = self.client.execute(
                """
                SELECT id, content, metadata, embedding
                FROM documents
                WHERE id = ?
                """,
                [document_id],
            ).fetchone()

            if result:
                return Document(
                    id=result[0],
                    content=result[1],
                    metadata=json.loads(result[2]),
                    embedding=Vector(value=result[3]),
                )
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get document {document_id}: {str(e)}")

    def get_all_documents(self) -> List[Document]:
        """Retrieve all documents from the store."""
        try:
            results = self.client.execute(
                """
                SELECT id, content, metadata, embedding
                FROM documents
                """
            ).fetchall()

            return [
                Document(
                    id=r[0],
                    content=r[1],
                    metadata=json.loads(r[2]),
                    embedding=Vector(value=r[3]),
                )
                for r in results
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to get all documents: {str(e)}")

    def update_document(self, document: Document) -> None:
        """Update an existing document."""
        try:
            embedding = self._prepare_vector(document)
            embedding_list = (
                embedding.value.tolist()
                if isinstance(embedding.value, np.ndarray)
                else embedding.value
            )

            self.client.execute(
                """
                UPDATE documents
                SET content = ?, metadata = ?, embedding = ?
                WHERE id = ?
                """,
                (
                    document.content,
                    json.dumps(document.metadata),
                    embedding_list,
                    document.id,
                ),
            )

            self._persist_to_disk()
        except Exception as e:
            raise RuntimeError(f"Failed to update document {document.id}: {str(e)}")

    def delete_document(self, document_id: str) -> None:
        """Delete a document by its ID."""
        try:
            self.client.execute("DELETE FROM documents WHERE id = ?", [document_id])
            self._persist_to_disk()
        except Exception as e:
            raise RuntimeError(f"Failed to delete document {document_id}: {str(e)}")

    def clear_documents(self) -> None:
        """Delete all documents from the store."""
        try:
            self.client.execute("DELETE FROM documents")
            self._persist_to_disk()
        except Exception as e:
            raise RuntimeError(f"Failed to clear documents: {str(e)}")

    def count_documents(self) -> int:
        """Get the total number of documents in the store."""
        try:
            result = self.client.execute("SELECT COUNT(*) FROM documents").fetchone()
            return result[0] if result else 0
        except Exception as e:
            raise RuntimeError(f"Failed to count documents: {str(e)}")

    def retrieve(self, query_vector: Vector, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve the top-k most similar documents to the query vector."""
        try:
            query_list = (
                query_vector.value.tolist()
                if isinstance(query_vector.value, np.ndarray)
                else query_vector.value
            )

            distance_func = {
                "cosine": "array_cosine_distance",
                "l2sq": "array_distance",
                "ip": "array_negative_inner_product",
            }.get(self.metric, "array_cosine_distance")

            results = self.client.execute(
                f"""
                SELECT
                    id,
                    content,
                    metadata,
                    embedding,
                    {distance_func}(embedding, ?) as distance
                FROM documents
                ORDER BY {distance_func}(embedding, ?)
                LIMIT ?
                """,
                [query_list, query_list, top_k],
            ).fetchall()

            return [
                {
                    "id": r[0],
                    "content": r[1],
                    "metadata": json.loads(r[2]),
                    "embedding": Vector(value=r[3]),
                    "distance": float(r[4]),
                }
                for r in results
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve similar documents: {str(e)}")

    def delete_document(self, document_id: str) -> None:
        """Delete a document by its ID."""
        try:
            self.client.execute("DELETE FROM documents WHERE id = ?", [document_id])
            self._persist_to_disk()
        except Exception as e:
            raise RuntimeError(f"Failed to delete document {document_id}: {str(e)}")

    def delete_documents(self, document_ids: List[str]) -> None:
        """Delete multiple documents by their IDs."""
        try:
            placeholders = ",".join(["?" for _ in document_ids])
            self.client.execute(
                f"DELETE FROM documents WHERE id IN ({placeholders})", document_ids
            )
            self._persist_to_disk()
        except Exception as e:
            raise RuntimeError(f"Failed to delete documents: {str(e)}")

    def model_dump_json(self, *args, **kwargs) -> str:
        """Prepare the instance for JSON serialization."""
        # Reset the client before serialization
        self.client = None
        return super().model_dump_json(*args, **kwargs)
