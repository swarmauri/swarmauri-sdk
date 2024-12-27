import json
import os
import sqlite3
import tempfile
from typing import List, Optional, Literal, Dict
import numpy as np
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_standard.documents.Document import Document
from swarmauri_standard.distances.CosineDistance import CosineDistance
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import (
    VectorStoreSaveLoadMixin,
)


class SqliteVectorStore(
    VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase
):
    type: Literal["SqliteVectorStore"] = "SqliteVectorStore"
    db_path: str = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name

    def __init__(self, db_path: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self._distance = CosineDistance()
        self.documents: List[Document] = []
        if db_path is not None:
            self.db_path = db_path

        # Create the SQLite database and table if they don't exist
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Create the documents table
        c.execute(
            """CREATE TABLE IF NOT EXISTS documents
                     (id TEXT PRIMARY KEY,
                      content TEXT,
                      metadata TEXT,
                      embedding BLOB)"""
        )

        conn.commit()
        conn.close()

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        self._insert_document(document)

    def _insert_document(self, document: Document):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Serialize metadata to JSON
        metadata_json = json.dumps(document.metadata)

        # Serialize embedding (specifically the value of the Vector)
        embedding_data = {
            "value": document.embedding.value  # Assuming embedding is of type Vector and has a 'value' attribute
        }
        embedding_json = json.dumps(embedding_data)

        # Insert the document into the documents table
        c.execute(
            "INSERT INTO documents (id, content, metadata, embedding) VALUES (?, ?, ?, ?)",
            (document.id, document.content, metadata_json, embedding_json),
        )
        conn.commit()
        conn.close()

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        for document in documents:
            self._insert_document(document)

    def get_document(self, document_id: str) -> Document:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            "SELECT id, content, metadata, embedding FROM documents WHERE id = ?",
            (document_id,),
        )
        row = c.fetchone()

        conn.close()

        if row:
            document_id, content, metadata_json, embedding_json = row
            metadata = json.loads(metadata_json)
            embedding_data = json.loads(embedding_json)
            embedding = Vector(
                value=embedding_data["value"]
            )  # Reconstruct the Vector object

            return Document(
                id=document_id, content=content, metadata=metadata, embedding=embedding
            )
        return None

    def get_all_documents(self) -> List[Document]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM documents")
        rows = c.fetchall()

        conn.close()

        return [
            Document(id=row[0], content=row[1], metadata=row[2], embedding=row[3])
            for row in rows
        ]

    def delete_document(self, document_id: str) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("DELETE FROM documents WHERE id = ?", (document_id,))

        conn.commit()
        conn.close()

    def update_document(self, document: Document) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """UPDATE documents 
               SET content = ?, metadata = ?, embedding = ? 
               WHERE id = ?""",
            (document.content, document.metadata, document.embedding, document.id),
        )

        conn.commit()
        conn.close()

    def retrieve(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, embedding FROM documents")
        rows = c.fetchall()
        conn.close()

        # Convert query vector to numpy array
        query_vector = np.array(query_vector, dtype=np.float32)

        results = []
        for row in rows:
            doc_id, embedding_json = row
            embedding = json.loads(embedding_json)
            vector = np.array(embedding["value"], dtype=np.float32)

            # Compute similarity (e.g., Euclidean distance)
            distance = np.linalg.norm(query_vector - vector)
            results.append((doc_id, distance))

        # Sort results by distance
        results.sort(key=lambda x: x[1])

        # Get top_k results
        top_results = [doc_id for doc_id, _ in results[:top_k]]
        return top_results

    def close(self):
        # Clean up the database file
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
