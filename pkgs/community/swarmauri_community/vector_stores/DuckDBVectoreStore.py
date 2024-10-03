from typing import List, Union, Literal, Optional
from pydantic import Field
from llama_index.vector_stores.duckdb import DuckDBVectorStore as LlamaIndexDuckDB
from llama_index.core import StorageContext, Document as LlamaDocument
from swarmauri.documents.concrete.Document import Document
from swarmauri.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding
from swarmauri.distances.concrete.CosineDistance import CosineDistance
from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import (
    VectorStoreSaveLoadMixin,
)


class DuckDBVectorStore(
    VectorStoreRetrieveMixin, VectorStoreSaveLoadMixin, VectorStoreBase
):
    type: Literal["DuckDBVectorStore"] = "DuckDBVectorStore"
    db_path: str = Field(default=":memory:")
    persist_dir: Optional[str] = Field(default=None)
    table_name: str = Field(default="vectors")
    client: Optional[LlamaIndexDuckDB] = Field(default=None, exclude=True)
    vector_size: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = Doc2VecEmbedding(vector_size=self.vector_size)
        self._distance = CosineDistance()
        self.connect()

    def connect(self):
        try:
            self.client = LlamaIndexDuckDB(
                database_name=self.db_path,
                table_name=self.table_name,
                persist_dir=self.persist_dir,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to DuckDB: {str(e)}")

    def disconnect(self):
        self.client = None

    def _convert_to_llama_doc(self, document: Document) -> LlamaDocument:
        if not document.embedding:
            self._embedder.fit([document.content])
            embedding = self._embedder.transform([document.content])[0].to_numpy()
            document.embedding = embedding.tolist()
        return LlamaDocument(
            text=document.content,
            metadata=document.metadata,
            embedding=document.embedding,
            id_=document.id,
        )

    def _convert_from_llama_doc(self, llama_doc: LlamaDocument) -> Document:
        return Document(
            id=llama_doc.id_,
            content=llama_doc.text,
            metadata=llama_doc.metadata,
            embedding=llama_doc.embedding,
        )

    def add_document(self, document: Document) -> None:
        llama_doc = self._convert_to_llama_doc(document)
        self.client.add([llama_doc])

    def add_documents(self, documents: List[Document]) -> None:
        llama_docs = [self._convert_to_llama_doc(doc) for doc in documents]
        self.client.add(llama_docs)

    def get_document(self, id: str) -> Union[Document, None]:
        results = self.client.get([id])
        if results:
            return self._convert_from_llama_doc(results[0])
        return None

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_embedding = self._embedder.infer_vector(query).value
        results = self.client.query(query_embedding, k=top_k)
        return [self._convert_from_llama_doc(doc) for doc in results]

    def delete_document(self, id: str) -> None:
        self.client.delete([id])

    def get_all_documents(self) -> List[Document]:
        all_docs = self.client.get_all()
        return [self._convert_from_llama_doc(doc) for doc in all_docs]

    def update_document(self, id: str, document: Document) -> None:
        llama_doc = self._convert_to_llama_doc(document)
        self.client.update([llama_doc])

    def clear_documents(self) -> None:
        self.client.delete_all()

    @classmethod
    def from_local(cls, db_path: str, persist_dir: Optional[str] = None, **kwargs):
        return cls(db_path=db_path, persist_dir=persist_dir, **kwargs)
